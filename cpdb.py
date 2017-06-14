import sqlite3


def __cp_label_result():
    db_from_file = 'db1-cp.sqlite3'
    db_to_file = 'db1.sqlite3'

    conn_from = sqlite3.connect(db_from_file)
    conn_to = sqlite3.connect(db_to_file)
    sql_from = 'SELECT * FROM yelp_labelresultv2'
    sql_to = 'INSERT INTO yelp_labelresultv2 (mention_id, cur_state, ' \
             'is_wrong_span, biz_id, username) values(?, ?, ?, ?, ?)'
    r = conn_from.execute(sql_from)
    for i, row in enumerate(r):
        print row
        conn_to.execute(sql_to, row[1:])
    conn_to.commit()


if __name__ == '__main__':
    __cp_label_result()
