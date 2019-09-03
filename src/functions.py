functions_name = {

    u"自定义函数":{
        "read_data":{
            "name":"read_data",
            "demo_code":"# 读取表格数据\n\ndata = read_data('50ETF')\nprint(data)\n"
        },

        "add_signal":{
            "name": "add_signal",
            "demo_code": "# 添加信号列\n\nresult = read_data('50ETF', 0)\nprint(result)\n"
        },

        "get_stock_ids":{
            "name": "get_stock_ids",
            "demo_code": "# 获取所有股票列表\n\nresult = get_stock_ids()\nprint(result)\n"
        },

        "get_stock":{
            "name": "get_stock",
            "demo_code": "# 获取股票实例\n\nstock_id = get_stock_ids()\nstock_item = get_stock(stock_id[1])\nprint(stock_item.daily.text)\n"
        },


    }





}