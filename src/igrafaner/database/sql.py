import time
from mysql import connector

from . import helper
from ..params import MySQL


def get_period_data(start: str, end: str):
    """
    Get the data in period.

    PicPath, X1, X2, Y1, Y2, PK_CompID, PartNo
    """

    [helper.validate_datetime_format(date) for date in (start, end)]
    conn = connector.connect(
        host=MySQL.host,
        port=MySQL.port,
        user=MySQL.user,
        password=MySQL.password,
        database=MySQL.database
    )
    # select PicPath,X1,X2,Y1,Y2,PK_CompID from vUnionTable where fdate>='2024-01-03' and fdate<'2024-01-04'
    sql_query = """\
        SELECT PicPath, X1, X2, Y1, Y2, PK_CompID, PartNo \
        FROM vUnionTable \
        WHERE vUnionTable.fdate BETWEEN %s AND %s"""

    try:
        with conn.cursor() as cursor:
            ts = time.time()
            cursor.execute(sql_query, (start, end))
            result = cursor.fetchall()
            te = time.time()
    except:
        conn.rollback()

    conn.close()
    print(f'Get {len(result)} data between {start} and {end} ({round(te-ts)}s)')
    return result


def write_ai_result(comp_id: str, ai_result: str):

    conn = connector.connect(
        host=MySQL.host,
        port=MySQL.port,
        user=MySQL.user,
        password=MySQL.password,
        database=MySQL.database
    )
    sql_query = """UPDATE Component SET AI_result = %s \
        WHERE PK_CompID = %s;"""

    try:
        with conn.cursor() as cursor:
            ts = time.time()
            cursor.execute(sql_query, (ai_result, int(comp_id)))
            conn.commit()
            te = time.time()
    except Exception as e:
        print(e)
        conn.rollback()

    conn.close()
    # print(f'Updated {comp_id} = {ai_result} ({round(te-ts)}s)')
