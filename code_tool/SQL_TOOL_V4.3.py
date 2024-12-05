import datetime
from tkinter import *
import re
from tkinter import font
import sqlparse
import pyperclip

# 关键字列表
keywords = ['select', 'from', 'where', 'and', 'or', 'left join', 'left outer join', 'join', 'by', 'on',
            'case', 'when', 'else', 'if', 'end', 'then', 'asc', 'desc', 'not', 'like', 'in', 'group',
            'order', 'grouping sets', 'grouping', 'rollup', 'full', 'distinct', 'is', 'null', 'union all',
            'union', 'having', 'between', 'exists', 'string', 'int', 'decimal', 'double', 'comment', 'create',
            'external', 'table', 'bigint', 'stored', 'as', 'orc', 'parquet', 'location', 'distribute', 'insert',
            'overwrite', 'partition', 'using', 'if', 'or', 'view', 'with', 'inner', 'msck', 'exists', 'vacuum',
            'analyze']


# 复制装饰器
def auto_copy(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        if current_copy_status == "open":
            sql = text.get("1.0", "end-1c")
            pyperclip.copy(sql)
            label_text = label.cget("text")
            if "已复制" not in label_text:
                label_text += ", 已复制至粘贴板!"
            label.config(text=label_text)

    return wrapper


@auto_copy
def on_convert_click():
    global current_case
    if current_case == "upper":
        convert_keywords("lower")
        current_case = "lower"
    else:
        convert_keywords("upper")
        current_case = "upper"


def on_copy_click():
    global current_copy_status
    if current_copy_status == "open":
        current_copy_status = "close"
        auto_copy_button.config(text="自动复制:已关闭", fg="red")
    else:
        current_copy_status = "open"
        auto_copy_button.config(text="自动复制:开启中", fg="green")


def convert_keywords(case):
    # 获取文本框中的SQL内容
    sql = text.get("1.0", "end-1c")

    # 使用正则表达式将SQL中的关键字转换为指定大小写
    pattern = re.compile(r'\b(' + '|'.join(keywords) + r')\b', re.IGNORECASE)
    if case == "upper":
        converted_sql = pattern.sub(lambda m: m.group().upper(), sql)
    else:
        converted_sql = pattern.sub(lambda m: m.group().lower(), sql)

    # 清空文本框内容并显示转换后的SQL
    text.delete("1.0", END)
    label.config(text="转换SQL成功")
    text.insert(END, converted_sql)
    # 高亮显示关键字
    highlight_keywords()


@auto_copy
def highlight_keywords():  # 高亮显示关键字
    # 配置关键字的样式
    text.tag_configure('keyword', font='TkDefaultFont 9 bold', foreground='red')

    # 获取文本框内容
    sql = text.get("1.0", "end-1c")

    for keyword in keywords:
        start_index = '1.0'
        while True:
            # 使用正则表达式搜索关键字，并为其添加样式
            start_index = text.search(rf'\y{keyword}\y', start_index, stopindex=END, count=1, nocase=True, regexp=True)
            if not start_index:
                break
            end_index = f"{start_index}+{len(keyword)}c"
            text.tag_add('keyword', start_index, end_index)
            start_index = end_index


def display_keywords():
    # 清空关键字列表框架中的内容
    keyword_text.delete("1.0", END)

    # 将关键字列表显示在关键字列表框架中
    for i, keyword in enumerate(keywords):
        keyword_text.insert(END, f"{i + 1}. {keyword}\n")


def add_keyword():
    # 获取新增关键字输入框中的内容
    new_keyword = new_keyword_entry.get().strip()

    if new_keyword:
        # 将新增关键字添加到关键字列表中
        keywords.append(new_keyword)

        # 清空新增关键字输入框
        new_keyword_entry.delete(0, END)

        # 更新关键字列表显示
        display_keywords()


def delete_keyword():
    # 获取删除关键字输入框中的内容
    index = delete_keyword_entry.get().strip()

    if index and index.isdigit() and int(index) <= len(keywords):
        # 删除指定索引的关键字
        del keywords[int(index) - 1]

        # 清空删除关键字输入框
        delete_keyword_entry.delete(0, END)

        # 更新关键字列表显示
        display_keywords()


@auto_copy
def reformat_sql():
    # 获取文本框中的SQL内容
    sql = text.get("1.0", "end-1c")

    # 使用 sqlparse 将 SQL 格式化
    formatted_sql = sqlparse.format(sql, reindent=True)

    # 清空文本框内容并显示转换后的SQL
    text.delete("1.0", END)
    label.config(text="格式化SQL成功")
    text.insert(END, formatted_sql)

    # 高亮显示关键字
    highlight_keywords()


def format_sql(sql_content):
    """将sql语句进行规范化，并去除sql中的注释，输入和输出均为字符串"""
    parse_str = sqlparse.format(sql_content, reindent=True, strip_comments=True)
    return parse_str


def extract_table_names():
    """从sql中提取对应的表名称，输出为列表"""
    sql_query = text.get("1.0", "end-1c")
    table_names = set()
    # 解析SQL语句
    parsed = sqlparse.parse(sql_query)
    # 正则表达式模式，用于匹配表名
    table_name_pattern = r'\bFROM\s+([^\s\(\)\,]+)|\bJOIN\s+([^\s\(\)\,]+)'
    # with 子句判断
    with_pattern = r'with\s+(\w+)\s+as'
    remove_with_name = []

    # 遍历解析后的语句块
    for statement in parsed:
        # 转换为字符串
        statement_str = str(statement).lower()

        # 将字符串中的特殊语法置空
        statement_str = re.sub('(substring|extract)\s*\(((.|\s)*?)\)', '', statement_str)

        # 查找匹配的表名
        matches = re.findall(table_name_pattern, statement_str, re.IGNORECASE)

        for match in matches:
            # 提取非空的表名部分
            for name in match:
                # if name and name not in not_contain_list:
                if name:
                    # 对于可能包含命名空间的情况，只保留最后一部分作为表名
                    # table_name = name.split('.')[-1]
                    # 去除表名中的特殊符号
                    table_name = re.sub('("|`|\'|;)', '', name)
                    table_names.add(table_name)
        # 处理特殊的with语句
        if 'with' in statement_str:
            match = re.search(with_pattern, statement_str)
            if match:
                result = match.group(1)
                remove_with_name.append(result)
    table_list = list(table_names)
    # 移除多余的表名
    if remove_with_name:
        table_list = list(set(table_list) - set(remove_with_name))

    # 创建新窗口
    table_window = Toplevel(root)
    table_window.title("提取的表名,双击即可选中")
    table_text = Text(table_window, height=20, width=50)
    table_text.pack()

    # 将数据插入到文本框中
    table_text.insert(END, "\n".join(table_list))


def on_entry1_change(event):
    if dt_entry.get():
        end_dt_entry.config(state="normal")
    else:
        end_dt_entry.delete(0, "end")
        end_dt_entry.config(state="disabled")


def date_click(mode):
    if mode == "today":
        date = datetime.date.today()
    else:
        date = datetime.date.today() - datetime.timedelta(days=1)
        end_dt_entry.config(state="normal")
    date_str = date.strftime("%Y%m%d")
    if mode == "today":
        end_dt_entry.delete(0, "end")  # 清空输入框内容
        end_dt_entry.insert(0, date_str)  # 将昨天的日期插入到输入框中
    else:
        dt_entry.delete(0, "end")  # 清空输入框内容
        dt_entry.insert(0, date_str)  # 将昨天的日期插入到输入框中


@auto_copy
def select(mode):
    sql = ""
    try:
        database_name, table_name = table_entry.get().split('.')
    except ValueError:
        sql += f'-- @@@@@ 未输入数据库名, 默认yishou_data库\n{"-" * 100}\n\n'
        database_name, table_name = ['yishou_data', table_entry.get()]
    if mode == "count":
        sql += f"SELECT count(1) FROM {database_name}.{table_name};"
    else:
        sql += f"SELECT * FROM {database_name}.{table_name};"
    dt2 = end_dt_entry.get().strip()
    dt = dt_entry.get().strip()
    if not dt2:
        if dt:
            sql = sql[:-1] + f" WHERE dt = {dt};"
    else:
        sql = sql[:-1] + f" WHERE dt BETWEEN {dt} AND {dt2};"

    text.delete("1.0", END)
    if mode == "select":
        limit_sql = sql.split('\n')[-1][:-1]
        sql += f"\t-- 全量\n\n{limit_sql} limit 100; -- 查看一百条"
    text.insert(END, sql)
    convert_keywords("upper")
    label.config(text=f"已生成{mode}查询语句")


@auto_copy
def sql_flatten():
    sql = text.get('1.0', END)  # 匹配SQL语句中的注释部分
    pattern = r"--.*?$|/\*.*?\*/"
    result = re.sub(pattern, "", sql, flags=re.DOTALL | re.MULTILINE)
    pattern = r"\s+"
    flatten_sql = re.sub(pattern, " ", result)

    text.delete("1.0", END)
    text.insert(END, flatten_sql)


@auto_copy
def table_backup():
    sql = ""
    try:
        database_name, table_name = table_entry.get().split('.')
    except ValueError:
        sql += f'-- @@@@@ 未输入数据库名, 默认yishou_data库\n{"-" * 100}\n\n'
        database_name, table_name = ['yishou_data', table_entry.get()]
    sql += f'create table {database_name}.{table_name}_backup like {database_name}.{table_name};-- 按照A表格式建B表\n\ninsert into {database_name}.{table_name}_backup select * from {database_name}.{table_name}; -- 全量插入数据'

    text.delete("1.0", END)
    text.insert(END, sql)
    convert_keywords("upper")
    label.config(text="已生成备份表格语句")


@auto_copy
def analyze_table():
    sql = ""
    try:
        database_name, table_name = table_entry.get().split('.')
    except ValueError:
        sql += f'-- @@@@@ 未输入数据库名, 默认yishou_data库\n{"-" * 100}\n\n'
        database_name, table_name = ['yishou_data', table_entry.get()]
    sql += f' vacuum full {database_name}.{table_name}; -- 清空脏页和缓存\n\n analyze {database_name}.{table_name}; -- 解析表'

    text.delete("1.0", END)
    text.insert(END, sql)
    convert_keywords("upper")
    label.config(text="已生成备份表格语句")


@auto_copy
def create_sql():
    sql = ""
    try:
        database_name, table_name = table_entry.get().split('.')
    except ValueError:
        sql += f'-- @@@@@ 未输入数据库名, 默认yishou_data库\n{"-" * 100}\n\n'
        database_name, table_name = ['yishou_data', table_entry.get()]
    sql += f"""-- {"*" * 10}分区表建表语句{"*" * 10}\nCREATE TABLE if not exists {database_name}.{table_name}(\n\t`字段名0` STRING COMMENT "注释",\n\t`字段名1` DECIMAL(16,2) COMMENT "注释",\n\t`字段名2` BIGINT COMMENT "注释",\n\t`字段名3` DOUBLE COMMENT "注释",\n\t`dt` STRING COMMENT "日期分区"\n)\nUSING parquet\nPARTITIONED BY (dt)\nCOMMENT "表格注释" ;"""
    sql += f"""\n\n\n\n{"-" * 100}\n-- {"*" * 10}普通表建表语句{"*" * 10}\nCREATE TABLE if not exists {database_name}.{table_name}(\n\t`字段名0` STRING COMMENT "注释",\n\t`字段名1` DECIMAL(16,2) COMMENT "注释",\n\t`字段名2` BIGINT COMMENT "注释",\n\t`字段名3` DOUBLE COMMENT "注释"\n)\nUSING parquet\nCOMMENT "表格注释" ;"""
    text.delete("1.0", END)
    text.insert(END, sql)
    convert_keywords("upper")
    label.config(text="已生成内部表建表语句")


@auto_copy
def dws_create_table():
    sql = ""
    try:
        database_name, table_name = table_entry.get().split('.')
    except ValueError:
        sql += f'-- @@@@@ 未输入数据库名, 默认yishou_data库\n{"-" * 100}\n\n'
        database_name, table_name = ['yishou_data', table_entry.get()]
    sql += f"""-- {"*" * 10}分区表建表语句{"*" * 10}\nCREATE FOREIGN TABLE if not exists {database_name}.{table_name}(\n\t`字段名0` character varying,\n\t`字段名1` double precision,\n\t`字段名2` BIGINT,\n\t`字段名3` text,\n\t`dt` character varying\n)SERVER obs_server OPTIONS(\n\tencoding 'utf8',\n\tfoldername '/yishou-bigdata/{database_name}.db/{table_name}/',\n\tformat 'orc'\n) DISTRIBUTE BY ROUNDROBIN\nPARTITION BY (dt) AUTOMAPPED;"""
    sql += f"""\n\n\n\n{"-" * 100}\n-- {"*" * 10}普通表建表语句{"*" * 10}\nCREATE FOREIGN TABLE if not exists {database_name}.{table_name}(\n\t`字段名0` character varying,\n\t`字段名1` double precision,\n\t`字段名2` BIGINT,\n\t`字段名3` text\n)SERVER obs_server OPTIONS(\n\tencoding 'utf8',\n\tfoldername '/yishou-bigdata/{database_name}.db/{table_name}/',\n\tformat 'orc'\n) DISTRIBUTE BY ROUNDROBIN;"""
    text.delete("1.0", END)
    text.insert(END, sql)
    convert_keywords("upper")
    label.config(text="已生成内部表建表语句")


@auto_copy
def dws_create_internal_table():
    sql = ""
    try:
        database_name, table_name = table_entry.get().split('.')
    except ValueError:
        sql += f'-- @@@@@ 未输入数据库名, 默认yishou_data库\n{"-" * 100}\n\n'
        database_name, table_name = ['yishou_data', table_entry.get()]
    sql += f"""-- {"*" * 10}分区表建表语句{"*" * 10}\nCREATE TABLE if not exists {database_name}.{table_name}(\n\t`字段名0` character varying,\n\t`字段名1` double precision,\n\t`字段名2` BIGINT,\n\t`字段名3` text,\n\t`dt` date\n) WITH (\norientation=column, \ncompression=low, \ncolversion=2.0, \nttl='5 years', \nperiod='1 days', \nenable_delta=false\n) \nDISTRIBUTE BY HASH(哈希字段) \nPARTITION BY RANGE (dt) ;"""
    sql += f"""\n\n\n\n{"-" * 100}\n-- {"*" * 10}普通表建表语句{"*" * 10}\nCREATE TABLE if not exists {database_name}.{table_name}(\n\t`字段名0` character varying,\n\t`字段名1` double precision,\n\t`字段名2` BIGINT,\n\t`字段名3` text\n) WITH (\norientation=column, \ncompression=low, \ncolversion=2.0, \nenable_delta=false\n) \nDISTRIBUTE BY HASH(哈希字段) ;"""
    text.delete("1.0", END)
    text.insert(END, sql)
    convert_keywords("upper")
    label.config(text="已生成内部表建表语句")


@auto_copy
def create_external_sql():
    sql = ""
    try:
        database_name, table_name = table_entry.get().split('.')
    except ValueError:
        sql += f'-- @@@@@ 未输入数据库名, 默认yishou_data库\n{"-" * 100}\n\n'
        database_name, table_name = ['yishou_data', table_entry.get()]
    sql += f"""-- {"*" * 10}分区表建表语句{"*" * 10}\nCREATE EXTERNAL TABLE if not exists {database_name}.{table_name}(\n\t`字段名0` STRING COMMENT "注释",\n\t`字段名1` DECIMAL(16,2) COMMENT "注释",\n\t`字段名2` BIGINT COMMENT "注释",\n\t`字段名3` DOUBLE COMMENT "注释"\n)\nSTORED AS ORC\nPARTITIONED BY (dt string comment "日期分区")\nCOMMENT "表格注释" \nLOCATION "obs://yishou-bigdata/{database_name}.db/{table_name}";"""
    sql += f"""\n\n\n\n{"-" * 100}\n-- {"*" * 10}普通表建表语句{"*" * 10}\nCREATE EXTERNAL TABLE if not exists {database_name}.{table_name}(\n\t`字段名0` STRING COMMENT "注释",\n\t`字段名1` DECIMAL(16,2) COMMENT "注释",\n\t`字段名2` BIGINT COMMENT "注释",\n\t`字段名3` DOUBLE COMMENT "注释"\n)\nSTORED AS ORC\nCOMMENT "表格注释" \nLOCATION "obs://yishou-bigdata/{database_name}.db/{table_name}";"""
    text.delete("1.0", END)
    text.insert(END, sql)
    convert_keywords("upper")
    label.config(text="已生成外部表建表语句")


@auto_copy
def join_judge():
    sql = text.get('1.0', END)

    # 使用正则表达式匹配JOIN和ON关键字，并计数
    join_count = len(re.findall(r"\bJOIN\b", sql))
    on_count = len(re.findall(r"\bON\b", sql))

    if join_count == on_count:
        label.config(text="每个JOIN语句都包含ON条件")
    else:
        label.config(text="至少有一个JOIN语句没有ON条件")
        # 找出缺少ON条件的具体JOIN语句
        joins = re.findall(r"\bJOIN\b\s+([a-zA-Z0-9_]+)", sql)
        ons = re.findall(r"\bON\b\s+([a-zA-Z0-9_.= ]+)", sql)
        missing_join = None
        for join in joins:
            found = False
            for on in ons:
                if join.strip() + ' ' in on:
                    found = True
                    break
            if not found:
                missing_join = join
                break
        print(f"缺少ON条件的JOIN语句是：{missing_join}")


def main_page():
    """主页面, 包含了主窗口, 主输入框的创建"""
    global label, text, root
    root = Tk()
    root.title('SQL小工具')
    font_style = font.Font(size=20)
    # 创建标签
    label = Label(root, text="请输入SQL语句: ")
    label['font'] = font_style
    label.grid(row=0, column=0, sticky=N + S + E + W, columnspan=15)
    # Part-1
    # 创建主窗口滚动条
    scrollbar = Scrollbar(root, orient=VERTICAL)
    scrollbar.grid(row=1, column=15, sticky=N + S + E, rowspan=15)
    hor_scrollbar = Scrollbar(root, orient=HORIZONTAL)
    hor_scrollbar.grid(row=16, column=0, sticky=W + E, columnspan=15)
    # 创建文本框，并关联滚动条
    frame = Frame(root)
    frame.grid(row=1, column=0, sticky=N + S + W + E, rowspan=15, columnspan=15)
    text = Text(frame, height=40, width=100, yscrollcommand=scrollbar.set, xscrollcommand=hor_scrollbar.set)
    text.grid(row=1, column=0, sticky=N + S + W + E, rowspan=14, columnspan=14)
    scrollbar.config(command=text.yview)
    hor_scrollbar.config(command=text.xview)


def button_page():
    """主页面下方的按键界面, 含各种对主页文本框处理的方法"""
    global auto_copy_button
    # Part-2
    # 创建按钮frame
    batton_frame = Frame(root)
    batton_frame.grid(row=17, column=0, sticky=N + S + W + E, rowspan=2, columnspan=15)
    # 创建清空按钮
    clear_button = Button(batton_frame, text="清空",
                          command=lambda: [text.delete("1.0", END), label.config(text="请输入SQL语句: ")])
    clear_button.grid(row=1, column=1, padx=20, pady=20)
    # 创建复制按钮
    copy_button = Button(batton_frame, text="复制",
                         command=lambda: [pyperclip.copy(text.get("1.0", "end-1c")), label.config(text="复制成功!")])
    copy_button.grid(row=1, column=2, padx=20, pady=20)
    # 创建粘贴按钮
    paste_button = Button(batton_frame, text="粘贴",
                          command=lambda: [text.delete("1.0", END), text.insert(END, pyperclip.paste()),
                                           label.config(text="已粘贴!")])
    paste_button.grid(row=1, column=3, padx=20, pady=20)
    # 创建关键字大写按钮
    upper_button = Button(batton_frame, text="关键字大小写", command=on_convert_click)
    upper_button.grid(row=1, column=4, padx=20, pady=20)
    # 创建格式化按钮
    reformat_button = Button(batton_frame, text="格式化", command=reformat_sql)
    reformat_button.grid(row=1, column=6, padx=20, pady=20)
    # 创建提取表名按钮
    reformat_button = Button(batton_frame, text="提取表名", command=extract_table_names)
    reformat_button.grid(row=1, column=7, padx=20, pady=20)
    # 创建自动复制按钮
    auto_copy_button = Button(batton_frame, text="自动复制:开启中", fg="green", command=on_copy_click)
    auto_copy_button.grid(row=1, column=8, padx=20, pady=20)


def keywords_page():
    """关键词页面, 可通过此处的按钮对关键字进行增减"""
    global keyword_text, new_keyword_entry, delete_keyword_entry
    # Part-3
    # 创建keyword_frame
    keyword_frame = Frame(root)
    keyword_frame.grid(row=14, column=16, columnspan=3, rowspan=3)
    # 创建关键字列表标签
    keyword_label = Label(keyword_frame, text="关键字列表:")
    keyword_label.grid(row=0, column=0)
    # 创建关键字列表文本框，并关联滚动条
    keyword_text = Text(keyword_frame, height=5, width=20)
    keyword_text.grid(row=0, column=1)
    # 创建关键字列表滚动条
    keyword_scrollbar = Scrollbar(keyword_frame, orient=VERTICAL, command=keyword_text.yview)
    keyword_scrollbar.grid(row=0, column=2)
    # 将关键字列表文本框与滚动条关联
    keyword_text.config(yscrollcommand=keyword_scrollbar.set)
    new_keyword_label = Label(keyword_frame, text="新增关键字:")
    new_keyword_label.grid(row=1, column=0, pady=20, sticky=S)
    new_keyword_entry = Entry(keyword_frame)
    new_keyword_entry.grid(row=1, column=1)
    add_keyword_button = Button(keyword_frame, text="新增", command=add_keyword)
    add_keyword_button.grid(row=1, column=2)
    delete_keyword_label = Label(keyword_frame, text="删除关键字索引:")
    delete_keyword_label.grid(row=2, column=0, sticky=N)
    delete_keyword_entry = Entry(keyword_frame)
    delete_keyword_entry.grid(row=2, column=1)
    delete_keyword_button = Button(keyword_frame, text="删除", command=delete_keyword)
    delete_keyword_button.grid(row=2, column=2)


def table_method_page():
    """表方法界面, 通过输入的表名, 进行快捷的表方法实现"""
    global table_entry, dt_entry, end_dt_entry
    # Part-4
    # 创建表格快捷操作frame
    table_frame = Frame(root)
    table_frame.grid(row=2, column=16, rowspan=11, columnspan=3)
    # 创建表名、分区输入框
    table_label = Label(table_frame, text="表名:")
    table_label.grid(row=0, column=0, padx=5, pady=1, sticky=N + W + E)
    table_entry = Entry(table_frame, width=20)
    table_entry.grid(row=0, column=1, padx=5, pady=1, sticky=N + W + E)
    paste_button = Button(table_frame, text="粘贴", font=("Arial", 8), command=lambda: [table_entry.delete(0, "end"), table_entry.insert(0, pyperclip.paste())])
    paste_button.grid(row=0, column=2, padx=5, pady=1, sticky=N + W + E)
    dt_label = Label(table_frame, text="起始分区:")
    dt_label.grid(row=1, column=0, padx=5, pady=1, sticky=N + W + E)
    dt_entry = Entry(table_frame, width=20)
    dt_entry.grid(row=1, column=1, padx=5, pady=1, sticky=N + W + E)
    yesterday_button = Button(table_frame, text="昨日", font=("Arial", 8), command=lambda: date_click("yesterday"))
    yesterday_button.grid(row=1, column=2, padx=5, pady=1, sticky=N + W + E)
    end_dt_label = Label(table_frame, text="结束分区:")
    end_dt_label.grid(row=2, column=0, padx=5, pady=1, sticky=N + W + E)
    end_dt_entry = Entry(table_frame, width=20)
    end_dt_entry.grid(row=2, column=1, padx=5, pady=1, sticky=N + W + E)
    today_button = Button(table_frame, text="今日", font=("Arial", 8), command=lambda: date_click("today"))
    today_button.grid(row=2, column=2, padx=5, pady=1, sticky=N + W + E)
    end_dt_entry.config(state="disabled")  # 初始状态下禁用第二个输入框
    dt_entry.bind("<KeyRelease>", on_entry1_change)
    # select * 语句按钮
    select_button = Button(table_frame, text='select * 语句', command=lambda: select("select"))
    select_button.grid(row=3, column=0, pady=10, sticky=W + E)
    # select count 语句按钮
    select_count_button = Button(table_frame, text='select count 语句', command=lambda: select("count"))
    select_count_button.grid(row=3, column=1, pady=10, sticky=E)
    # DLI外部表建表 语句
    create_external_button = Button(table_frame, text='DLI外部表建表 语句', command=create_external_sql)
    create_external_button.grid(row=4, column=0, pady=10, sticky=E)
    # DLI内部表建表 语句
    create_button = Button(table_frame, text='DLI内部表建表 语句', command=create_sql)
    create_button.grid(row=4, column=1, pady=10, sticky=E)
    # SQL语句打平
    sql_flatten_button = Button(table_frame, text='SQL语句打平', command=sql_flatten)
    sql_flatten_button.grid(row=5, column=0, pady=10, sticky=E)
    # 备份表格
    table_backup_button = Button(table_frame, text='备份表格', command=table_backup)
    table_backup_button.grid(row=5, column=1, pady=10, sticky=E)
    # DWS分析表格
    analyze_table_button = Button(table_frame, text='DWS分析表格', command=analyze_table)
    analyze_table_button.grid(row=6, column=0, pady=10, sticky=E)
    # DWS跨源表建表
    dws_create_table_button = Button(table_frame, text='DWS跨源表建表', command=dws_create_table)
    dws_create_table_button.grid(row=6, column=1, pady=10, sticky=E)
    # 笛卡尔积判断
    dws_create_table_button = Button(table_frame, text='笛卡尔积判断(有bug)', command=join_judge)
    dws_create_table_button.grid(row=7, column=0, pady=10, sticky=E)
    # 笛卡尔积判断
    dws_create_table_button = Button(table_frame, text='DWS内部表建表', command=dws_create_internal_table)
    dws_create_table_button.grid(row=7, column=1, pady=10, sticky=E)


if __name__ == '__main__':
    main_page()  # 主页面
    button_page()  # 按钮页面
    keywords_page()  # 关键词页面
    table_method_page()  # 表方法页面

    # 初始化关键字列表显示
    display_keywords()

    # 初始化按键
    current_case = "lower"
    current_copy_status = 'open'

    root.mainloop()
