import os

SPLIT_SEPARATOR = ","
SPECIAL_CHARS = ["/", "\\", ":", "*", "?", "\"", "<", ">", "|"]

PAY_MODE = {
    "ALIPAY": {
        "name": "alipay",
        "encoding":  "gbk",
        "del_from": -3,
        "del_to": -1,
        "condition": 3,
        "from_line": 1
    },
    "WECHAT": {
        "name": "wechat",
        "encoding":  "utf8",
        "del_from": -4,
        "del_to": -1,
        "condition": 4,
        "from_line": 16
    },
}


def read_bill(filepath, mode):
    filename = os.path.splitext(
        os.path.basename(os.path.realpath(filepath)))[0]

    from_line = mode.get("from_line")
    del_from = mode.get("del_from")
    del_to = mode.get("del_to")
    name = mode.get("name")
    condition = mode.get("condition")
    encoding = mode.get("encoding")

    with open(filepath, "rt", encoding=encoding) as f:
        valid_lines = []
        filed_items = None
        for i, line in enumerate(f.readlines()):
            # 提取字段
            fileds = [filed.strip() for filed in line.split(SPLIT_SEPARATOR)]
            # 剔除最后一个分割出来的无效字段
            if fileds[-1] == "":
                fileds.pop()
            # 删除无用字段
            del fileds[del_from:del_to]
            if name == "wechat":
                fileds.pop()
            # 处理有效字段
            if len(fileds) > condition:
                if i == from_line:
                    filed_items = fileds
                elif i > from_line:
                    valid_lines.append(fileds)

        # 处理有效数据并按照字段排序
        for i in range(len(filed_items)):
            v = sorted(valid_lines, key=lambda x: x[i])
            output = "%s#%s.csv" % (filename, filed_items[i])
            for char in SPECIAL_CHARS:
                output = output.replace(char, "")
            output = "./output/" + output
            with open(output, "wt", encoding=encoding) as f:
                for line in v:
                    line[0], line[i] = line[i], line[0]
                    content = [l + "," for l in line]
                    f.writelines(content)
                    f.write("\n")
            print(output)


if __name__ == "__main__":
    os.makedirs("./output", exist_ok=True)
    files = 0
    for filename in os.listdir("./"):
        filepath = os.path.abspath(filename)
        if os.path.isfile(filepath) and os.path.splitext(filepath)[-1] == ".csv":
            if filename.find("alipay") > -1:
                read_bill(filepath, PAY_MODE.get("ALIPAY"))
                files += 1
            elif filename.find("微信") > -1:
                read_bill(filepath, PAY_MODE.get("WECHAT"))
                files += 1
    if files == 0:
        print("未找到账单文件")
    else:
        print("已处理%s件账单" % files)
