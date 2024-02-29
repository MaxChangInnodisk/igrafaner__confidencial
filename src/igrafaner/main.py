import argparse
import tqdm


def get_args() -> argparse.Namespace:
    """
    Build argparser for CLI user

    Returns:
        argparse.Namespace: the namesapce with arguments
    """
    parser = argparse.ArgumentParser()

    mysql_group = parser.add_argument_group(
        'MySql Group', 'the setting of the MySQL')

    mysql_group.add_argument(
        "--mysql-host", default="127.0.0.1", type=str, help="the IP address of the MySQL")
    mysql_group.add_argument(
        "--mysql-port", default="3306", type=str, help="the Port number of the MySQL")
    mysql_group.add_argument(
        "--mysql-username", default="max", type=str, help="the username of the MySQL")
    mysql_group.add_argument(
        "--mysql-password", default="max", type=str, help="the password of the MySQL")
    mysql_group.add_argument(
        "--mysql-database", default="grafana", type=str, help="the database name of the MySQL")

    data_group = parser.add_argument_group(
        'Data Group', 'the setting of the data in MySQL')
    data_group.add_argument(
        "--start-time", default="2023-09-02 00:52:10", type=str, help="the start time in period data"
    )
    data_group.add_argument(
        "--end-time", default="2023-09-02 00:52:30", type=str, help="the end time in period data"
    )

    onnx_group = parser.add_argument_group(
        'ONNX Group for AI Inference', 'the setting of the AI')
    onnx_group.add_argument(
        "--golden-folder", required=True, help="the path to golden folder"
    )
    onnx_group.add_argument(
        "--model-path", required=True, help="the path to onnx model"
    )

    mount_group = parser.add_argument_group(
        'Mount data for AI Inference', 'the setting of the shared disk')
    mount_group.add_argument(
        "--mount-folder", required=True, help="the path to shared disk folder with XML and MAP"
    )

    args = parser.parse_args()
    return args


def cli():
    import igrafaner as igra
    from collections import Counter

    args = get_args()

    # Init StopWatch
    w_e2e, w_samp, w_gold, w_infer = \
        [igra.helper.StopWatch() for _ in range(4)]
    
    w_e2e.split_start()
    
    # Get data from mysql
    igra.params.MySQL.host = args.mysql_host
    igra.params.MySQL.port = args.mysql_port
    igra.params.MySQL.user = args.mysql_username
    igra.params.MySQL.password = args.mysql_password
    igra.params.MySQL.database = args.mysql_database

    mysql_data = igra.database.get_period_data(
        start=args.start_time,
        end=args.end_time)
    num_mysql_data = len(mysql_data)

    # Init golden_parser and model
    golden_parser = igra.parser.GoldenParser(root=args.golden_folder)
    model = igra.model.OnnxSiamese(model_path=args.model_path)

    # Progress log
    def print_progress(cur, limit, func=print, *args, **kwargs):
        content = '[IGRA] {:03}% ({:06}/{:06}) PASS: {:06}, NG: {:06}, None: {:06}'.format(
            int((cur/limit)*100), cur, limit, pass_comp.count, ng_comp.count,
            err_gold.count + err_samp.count + err_infer.count)
        func(content, **kwargs)

    # Init Custom list
    err_cmod, err_samp, err_gold, err_infer, ng_comp, pass_comp \
        = [igra.helper.FailedCompDict() for _ in range(6)]

    w_e2e.split_start()

    for idx, data in enumerate(mysql_data):

        print_progress(cur=idx, limit=num_mysql_data, func=print, end='\r')

        # Init ai_result
        pic_path, x1, x2, y1, y2, comp_id, part_no, cmodel = data
        comp_id = str(comp_id)
        ai_result = "None"

        # Not supported cModel
        if not golden_parser.check_cmodel(cmodel=cmodel):
            err_cmod[comp_id] = {
                "type": igra.error.CModelNotFound.__name__,
                "message": "Not supported cModel"
            }
            continue

        # No specific part number ( no golden )
        if not golden_parser.check_part_no(part_no):
            err_gold[comp_id] = {
                "type": igra.error.PartNumberNotFound.__name__,
                "message": "Unpaired part_no"
            }
            igra.database.write_ai_result(comp_id=comp_id, ai_result=ai_result)
            continue

        # Get sample
        w_samp.split_start()
        try:
            sc = igra.parser.SampleComponent(
                src_path=pic_path,
                xxyy=[x1, x2, y1, y2],
                uid=comp_id,
                part_no=part_no,
                mount_folder=args.mount_folder)
        except Exception as e:
            err_samp[comp_id] = {
                "type": type(e).__name__,
                "message": f"Capture sample failed. ({e})"
            }
            igra.database.write_ai_result(comp_id=comp_id, ai_result=ai_result)
            continue
        w_samp.split_stop()

        # Get golden
        w_gold.split_start()
        try:
            gp = golden_parser.get_golden(
                part_no=sc.part_no, light_source=sc.light_source)
        except Exception as e:
            err_gold[comp_id] = {
                "type": type(e).__name__,
                "message": f"Capture golden failed. ({e})"
            }
            igra.database.write_ai_result(comp_id=comp_id, ai_result=ai_result)
            continue
        w_gold.split_stop()

        # Do inference
        w_infer.split_start()
        try:
            result = model.inference(sample=sc.buffer, golden=gp.buffer)[0]
            if result < float(gp.threshold):
                pass_comp.append(comp_id)
                ai_result = "OK"
            else:
                ng_comp.append(comp_id)
                ai_result = "NG"

        except Exception as e:
            err_infer[comp_id] = {
                "type": type(e).__name__,
                "message": f"Inference failed. ({e})"
            }
            igra.database.write_ai_result(comp_id=comp_id, ai_result=ai_result)
            continue
        w_infer.split_stop()

        # Write data
        igra.database.write_ai_result(comp_id=comp_id, ai_result=ai_result)

    # Record e2e cost time
    w_e2e.split_stop()

    print_progress(cur=num_mysql_data, limit=num_mysql_data,
                   func=print, end='\n')
    igra.logger.info('Information')
    igra.logger.info(f'- [ Data ] {num_mysql_data}')
    igra.logger.info(f'- [ Cost ] {w_e2e.total:.03f}s')
    igra.logger.info('AI Results')
    igra.logger.info(f'- [ {"OK":<4} ] {pass_comp.count}')
    igra.logger.info(f'- [ {"NG":<4} ] {ng_comp.count}')
    igra.logger.info(
        f'- [ {"None":<4} ] {err_gold.count+err_samp.count+err_infer.count} ( SampleErr: {err_samp.count}, GoldenErr: {err_gold.count}, InferErr: {err_infer.count})')

    igra.logger.info('Error Message')
    igra.logger.info(f'cModel')
    for err_type_name, err_type_uids in err_cmod.types.items():
        igra.logger.info(f'- [{err_type_name}] {len(err_type_uids)}')

    igra.logger.info(f'Sample')
    for err_type_name, err_type_uids in err_samp.types.items():
        igra.logger.info(f'- [{err_type_name}] {len(err_type_uids)}')

    igra.logger.info(f'Golden')
    for err_type_name, err_type_uids in err_gold.types.items():
        igra.logger.info(f'- [{err_type_name}] {len(err_type_uids)}')

    igra.logger.info(f'Inference Throughput ( E2E )')
    igra.logger.info(
        f'- [ EndToEnd__Cost ] min {w_e2e.min:.03f}s ; max {w_e2e.max:.03f}s ; avg {w_e2e.avg:.03f}s')
    igra.logger.info(
        f'- [ Capture_Sample ] min {w_samp.min:.03f}s ; max {w_samp.max:.03f}s ; avg {w_samp.avg:.03f}s')
    igra.logger.info(
        f'- [ Capture_Golden ] min {w_gold.min:.03f}s ; max {w_gold.max:.03f}s ; avg {w_gold.avg:.03f}s')
    igra.logger.info(
        f'- [ ONNX_inference ] min {w_infer.min:.03f}s ; max {w_infer.max:.03f}s ; avg {w_infer.avg:.03f}s')


if __name__ == "__main__":
    cli()
