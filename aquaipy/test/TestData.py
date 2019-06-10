
class TestData:

    @staticmethod
    def primary_mac_hydra52hd():
        return "D89760036700"

    @staticmethod
    def primary_mac_hydra26hd():
        return "D8976003AAAA"
 
    @staticmethod
    def primary_mac_primehd():
        return "D8976004AAAA"
    
    @staticmethod
    def identity_hydra52hd():
        return {
        "serial_number": "D89760036700",
        "parent": "",
        "firmware": "2.2.0",
        "product": "Hydra FiftyTwo",
        "product_type": "Standard",
        "product_sub_type": "",
        "product_color": "black",
        "product_hw_rev": 4,
        "cpu": "RT5350",
        "img": "prime",
        "mfg_date_utc": "2017-05-09 15:18:50",
        "mfg_date": "2017-05-10 01:18:50",
        "response_code": 0
    }

    @staticmethod
    def identity_hydra26hd(): 
        
        return {
        "serial_number": "D8976003AAAA",
        "parent": "",
        "firmware": "2.2.0",
        "product": "Hydra TwentySix",
        "product_type": "Standard",
        "product_sub_type": "",
        "product_color": "black",
        "product_hw_rev": 4,
        "cpu": "RT5350",
        "img": "prime",
        "mfg_date_utc": "2017-05-09 15:18:50",
        "mfg_date": "2017-05-10 01:18:50",
        "response_code": 0
    }

    @staticmethod
    def identity_primehd():

        return {
        "serial_number": "D8976004AAAA",
        "parent": "",
        "firmware": "2.2.0",
        "product": "Prime HD",
        "product_type": "Standard",
        "product_sub_type": "",
        "product_color": "white",
        "product_hw_rev": 4,
        "cpu": "RT5350",
        "img": "prime",
        "mfg_date_utc": "2017-08-23 16:21:22",
        "mfg_date": "2017-08-24 02:21:22",
        "response_code": 0
    }

    @staticmethod
    def identity_hydra26hd_unsupported_firmware(): 
        
        return {
        "serial_number": "D8976003AAAA",
        "parent": "",
        "firmware": "10.0.0",
        "product": "Hydra TwentySix",
        "product_type": "Standard",
        "product_sub_type": "",
        "product_color": "black",
        "product_hw_rev": 4,
        "cpu": "RT5350",
        "img": "prime",
        "mfg_date_utc": "2017-05-09 15:18:50",
        "mfg_date": "2017-05-10 01:18:50",
        "response_code": 0
    }

    @staticmethod
    def identity_not_parent():

        return {
        "serial_number": "D8976003BBBB",
        "parent": "hydra26-D8976003AAAA",
        "firmware": "2.2.0",
        "product": "Hydra TwentySix",
        "product_type": "Standard",
        "product_sub_type": "",
        "product_color": "black",
        "product_hw_rev": 4,
        "cpu": "RT5350",
        "img": "prime",
        "mfg_date_utc": "2017-06-27 18:12:33",
        "mfg_date": "2017-06-28 04:12:33",
        "response_code": 0
    }

    @staticmethod
    def schedule_enabled():
        return{
        "enable": True,
        "response_code": 0
    }

    @staticmethod
    def schedule_disabled():
        return {
        "enable": False,
        "response_code": 0
    }

    @staticmethod
    def get_colors():
        return {
        "deep_red",
        "uv",
        "violet",
        "cool_white",
        "green",
        "blue",
        "royal"
    }

    @staticmethod
    def colors_1():
        return {
        "deep_red": 0,
        "uv": 0,
        "violet": 0,
        "cool_white": 0,
        "green": 0,
        "blue": 0,
        "royal": 0,
        "response_code": 0
    }
    
    @staticmethod
    def colors_2():
        return {
        "deep_red": 1000,
        "uv": 1000,
        "violet": 1000,
        "cool_white": 1000,
        "green": 1000,
        "blue": 1000,
        "royal": 1000,
        "response_code": 0
    }

    @staticmethod
    def colors_3(): 
        return {
        "deep_red": 0,
        "uv": 424,
        "violet": 1262,
        "cool_white": 0,
        "green": 0,
        "blue": 0,
        "royal": 1435,
        "response_code": 0
    }
    
    @staticmethod
    def set_colors_1():
        return {
        "deep_red": 0,
        "uv": 0,
        "violet": 0,
        "cool_white": 0,
        "green": 0,
        "blue": 0,
        "royal": 0,
    }
    
    @staticmethod
    def set_colors_2():
        return {
        "deep_red": 100,
        "uv": 100,
        "violet": 100,
        "cool_white": 100,
        "green": 100,
        "blue": 100,
        "royal": 100,
    }

    @staticmethod
    def set_colors_3(): 
        return {
        "deep_red": 0,
        "uv": 42,
        "violet": 105,
        "cool_white": 0,
        "green": 0,
        "blue": 0,
        "royal": 117,
    }

    @staticmethod
    def get_colors_3():
        return {
        "deep_red": 0,
        "uv": 42.4,
        "violet": 104.78739920732541,
        "cool_white": 0,
        "green": 0,
        "blue": 0,
        "royal": 117.23028298727394,
    }
    
    @staticmethod
    def set_colors_max_hd_primehd():
        return {
        "deep_red": 100,
        "uv": 102.04256965944272,
        "violet": 100.28212839791787,
        "cool_white": 76,
        "green": 100,
        "blue": 108.0932966023875111,
        "royal": 116.8702380952381
    }
    
    @staticmethod
    def set_colors_max_hd_hydra26hd():
        return {
        "deep_red": 2.6,
        "uv": 104.54843191196699,
        "violet": 104.84221675550089,
        "cool_white": 114.42251610715496,
        "green": 3.4,
        "blue": 104.73310638297872,
        "royal": 111.209586403215
    }
    
    @staticmethod
    def set_colors_max_hd_hydra52hd():
        return {
        "deep_red": 100,
        "uv": 156.395521648667,
        "violet": 157.8024373328049,
        "cool_white": 100,
        "green": 100,
        "blue": 100,
        "royal": 62.1490263045547
    }
    
    @staticmethod
    def set_colors_hd_exceeded_primehd(): 
        return {
        "deep_red": 0,
        "uv": 100,
        "violet": 100,
        "cool_white": 113,
        "green": 100,
        "blue": 100,
        "royal": 108,
    }

    @staticmethod
    def set_colors_hd_exceeded_hydra26hd(): 
        return {
        "deep_red": 0,
        "uv": 100,
        "violet": 100,
        "cool_white": 113,
        "green": 100,
        "blue": 100,
        "royal": 108,
    }
    
    @staticmethod
    def set_colors_hd_exceeded_mixed(): 
        return {
        "deep_red": 123.63069306930693,
        "uv": 116.00985552115583,
        "violet": 112.89953730480046,
        "cool_white": 21,
        "green": 125.43627075351213,
        "blue": 109.04997704315886,
        "royal": 118.12559523809523,
    }

    @staticmethod
    def set_result_colors_3_hydra26hd(): 
        return {
        "deep_red": 0,
        "uv": 420,
        "violet": 1274,
        "cool_white": 0,
        "green": 0,
        "blue": 0,
        "royal": 1429
    }
    
    @staticmethod
    def set_result_colors_3_primehd(): 
        return {
        "deep_red": 0,
        "uv": 420,
        "violet": 1319,
        "cool_white": 0,
        "green": 0,
        "blue": 0,
        "royal": 1772
    }

    @staticmethod
    def set_result_colors_max_hd_primehd(): 
        return {
        "deep_red": 1000,
        "uv": 1105,
        "violet": 1018,
        "cool_white": 760,
        "green": 1000,
        "blue": 1736,
        "royal": 1766
    }

    @staticmethod
    def set_result_colors_max_hd_hydra26hd(): 
        return {
        "deep_red": 26,
        "uv": 1253,
        "violet": 1265,
        "cool_white": 1392,
        "green": 34,
        "blue": 1299,
        "royal": 1283
    }
    
    @staticmethod
    def set_result_colors_max_hd_hydra52hd(): 
        return {
        "deep_red": 1000,
        "uv": 2000,
        "violet": 2000,
        "cool_white": 1000,
        "green": 1000,
        "blue": 1000,
        "royal": 621
    }
    
    @staticmethod
    def result_intensities_0p(): 
        return {
        "deep_red": 0,
        "uv": 0,
        "violet": 0,
        "cool_white": 0,
        "green": 0,
        "blue": 0,
        "royal": 0
    }
 
    @staticmethod
    def result_intensities_33_333p(): 
        return {
        "deep_red": 333,
        "uv": 333,
        "violet": 333,
        "cool_white": 333,
        "green": 333,
        "blue": 333,
        "royal": 333
    }
    
    @staticmethod
    def result_intensities_100p(): 
        return {
        "deep_red": 1000,
        "uv": 1000,
        "violet": 1000,
        "cool_white": 1000,
        "green": 1000,
        "blue": 1000,
        "royal": 1000
    }
    
    @staticmethod
    def result_intensities_105p_hydra26hd(): 
        return {
        "deep_red": 1059,
        "uv": 1278,
        "violet": 1274,
        "cool_white": 1136,
        "green": 1046,
        "blue": 1316,
        "royal": 1126
    }
    
    @staticmethod
    def result_intensities_107_5893p_hydra26hd(): 
        return {
        "deep_red": 1090,
        "uv": 1422,
        "violet": 1415,
        "cool_white": 1206,
        "green": 1069,
        "blue": 1479,
        "royal": 1192
    }
    
    @staticmethod
    def result_intensities_110p_hydra26hd(): 
        return {
        "deep_red": 1118,
        "uv": 1556,
        "violet": 1547,
        "cool_white": 1272,
        "green": 1092,
        "blue": 1632,
        "royal": 1252
    }
    
    @staticmethod
    def result_intensities_105p_primehd(): 
        return {
        "deep_red": 1174,
        "uv": 1257,
        "violet": 1319,
        "cool_white": 1241,
        "green": 1162,
        "blue": 1455,
        "royal": 1227
    }
    
    @staticmethod
    def result_intensities_107_5893p_primehd(): 
        return {
        "deep_red": 1264,
        "uv": 1390,
        "violet": 1484,
        "cool_white": 1366,
        "green": 1246,
        "blue": 1690,
        "royal": 1345
    }
    
    @staticmethod
    def result_intensities_110p_primehd(): 
        return {
        "deep_red": 1348,
        "uv": 1514,
        "violet": 1638,
        "cool_white": 1482,
        "green": 1324,
        "blue": 1909,
        "royal": 1454
    }

    
    @staticmethod
    def result_mw_hydra26hd_0(): 
        return {
        "deep_red": 0,
        "uv": 0,
        "violet": 0,
        "cool_white": 0,
        "green": 0,
        "blue": 0,
        "royal": 0
    }
    
    @staticmethod
    def result_mw_primehd_0(): 
        return {
        "deep_red": 0,
        "uv": 0,
        "violet": 0,
        "cool_white": 0,
        "green": 0,
        "blue": 0,
        "royal": 0
    }
    
    @staticmethod
    def result_mw_hydra26hd_500(): 
        return {
        "deep_red": 1884.0,
        "uv": 3635.0,
        "violet": 3658.5,
        "cool_white": 11796.0,
        "green": 2095.0,
        "blue": 9987.5,
        "royal": 11944.0
    }
    
    @staticmethod
    def result_mw_primehd_500(): 
        return {
        "deep_red": 1313.0,
        "uv": 1938.0,
        "violet": 1729.0,
        "cool_white": 6378.0,
        "green": 1566.0,
        "blue": 4356.0,
        "royal": 6720.0
    }

    @staticmethod
    def result_mw_hydra26hd_1000(): 
        return {
        "deep_red": 3768.0,
        "uv": 7270.0,
        "violet": 7317.0,
        "cool_white": 23592.0,
        "green": 4190.0,
        "blue": 19975.0,
        "royal": 23888.0
    }
    
    @staticmethod
    def result_mw_primehd_1000(): 
        return {
        "deep_red": 2626.0,
        "uv": 3876.0,
        "violet": 3458.0,
        "cool_white": 12756.0,
        "green": 3132.0,
        "blue": 8712.0,
        "royal": 13440.0
    }

    @staticmethod
    def result_mw_hydra26hd_1500(): 
        return {
        "deep_red": 5359.0,
        "uv": 7923.5,
        "violet": 7985.5,
        "cool_white": 27932.0,
        "green": 6479.5,
        "blue": 21556.0,
        "royal": 28619.0
    }
 
    @staticmethod
    def result_mw_primehd_1500(): 
        return {
        "deep_red": 3003.0,
        "uv": 4253.0,
        "violet": 3729.0,
        "cool_white": 14078.0,
        "green": 3616.0,
        "blue": 9191.0,
        "royal": 14920.0
    }
 
    @staticmethod
    def result_mw_hydra26hd_2000(): 
        return {
        "deep_red": 6950.0,
        "uv": 8577.0,
        "violet": 8654.0,
        "cool_white": 32272.0,
        "green": 8769.0,
        "blue": 23137.0,
        "royal": 33350.0
    }
 
    @staticmethod
    def result_mw_primehd_2000(): 
        return {
        "deep_red": 3380.0,
        "uv": 4630.0,
        "violet": 4000.0,
        "cool_white": 15400.0,
        "green": 4100.0,
        "blue": 9670.0,
        "royal": 16400.0
    }
 
    @staticmethod
    def server_error():
        return {
        "response_code":11
    }

    @staticmethod
    def server_success():
        return {
            "response_code":0
            }
    
    @staticmethod
    def power_hydra52hd():
        return {
        "devices":[
            {
                "serial_number":"D89760036700",
                "type":"Hydra FiftyTwo",
                "max_power":120000,
                "hd":{
                    "royal":61380,
                    "cool_white":59395,
                    "deep_red":12791,
                    "violet":15927,
                    "uv":15785,
                    "blue":42583,
                    "green":16139
                },
                "normal":{
                    "royal":30451,
                    "cool_white":30485,
                    "deep_red":4055,
                    "violet":10093,
                    "uv":10093,
                    "blue":30773,
                    "green":4050
                }
            }
        ],
        "response_code":0
    }

    @staticmethod
    def power_hydra26hd():
        return {
        "devices": [
            {
                "serial_number": "D8976003AAAA",
                "type": "Hydra TwentySix",
                "max_power": 90000,
                "hd": {
                    "blue": 23137,
                    "cool_white": 32272,
                    "violet": 8654,
                    "green": 8769,
                    "deep_red": 6950,
                    "royal": 33350,
                    "uv": 8577
                },
                "normal": {
                    "blue": 19975,
                    "cool_white": 23592,
                    "violet": 7317,
                    "green": 4190,
                    "deep_red": 3768,
                    "royal": 23888,
                    "uv": 7270
                }
            }
        ],
        "response_code": 0
    }


    @staticmethod
    def power_primehd():
        return {
        "devices": [
            {
                "serial_number": "D8976004AAAA",
                "type": "Prime HD",
                "max_power": 48000,
                "hd": {
                    "royal": 16400,
                    "cool_white": 15400,
                    "green": 4100,
                    "violet": 4000,
                    "uv": 4630,
                    "blue": 9670,
                    "deep_red": 3380
                },
                "normal": {
                    "royal": 13440,
                    "cool_white": 12756,
                    "green": 3132,
                    "violet": 3458,
                    "uv": 3876,
                    "blue": 8712,
                    "deep_red": 2626
                }
            }
        ],
        "response_code": 0
    }

    @staticmethod
    def power_two_hd_devices():
        return {
        "devices": [
            {
                "serial_number": "D8976003AAAA",
                "type": "Hydra TwentySix",
                "max_power": 90000,
                "hd": {
                    "blue": 23137,
                    "cool_white": 32272,
                    "violet": 8654,
                    "green": 8769,
                    "deep_red": 6950,
                    "royal": 33350,
                    "uv": 8577
                },
                "normal": {
                    "blue": 19975,
                    "cool_white": 23592,
                    "violet": 7317,
                    "green": 4190,
                    "deep_red": 3768,
                    "royal": 23888,
                    "uv": 7270
                }
            },
            {
                "serial_number": "D8976003BBBB",
                "type": "Hydra TwentySix",
                "max_power": 90000,
                "hd": {
                    "blue": 23137,
                    "cool_white": 32272,
                    "violet": 8654,
                    "green": 8769,
                    "deep_red": 6950,
                    "royal": 33350,
                    "uv": 8577
                },
                "normal": {
                    "blue": 19975,
                    "cool_white": 23592,
                    "violet": 7317,
                    "green": 4190,
                    "deep_red": 3768,
                    "royal": 23888,
                    "uv": 7270
                }
            }
        ],
        "response_code": 0
    }


    @staticmethod
    def power_mixed_hd_devices():
        return {
        "devices": [
            {
                "serial_number": "D8976004AAAA",
                "type": "Prime HD",
                "max_power": 48000,
                "hd": {
                    "royal": 16400,
                    "cool_white": 15400,
                    "green": 4100,
                    "violet": 4000,
                    "uv": 4630,
                    "blue": 9670,
                    "deep_red": 3380
                },
                "normal": {
                    "royal": 13440,
                    "cool_white": 12756,
                    "green": 3132,
                    "violet": 3458,
                    "uv": 3876,
                    "blue": 8712,
                    "deep_red": 2626
                }
            },
            {
                "serial_number": "D8976003BBBB",
                "type": "Hydra TwentySix",
                "max_power": 90000,
                "hd": {
                    "blue": 23137,
                    "cool_white": 32272,
                    "violet": 8654,
                    "green": 8769,
                    "deep_red": 6950,
                    "royal": 33350,
                    "uv": 8577
                },
                "normal": {
                    "blue": 19975,
                    "cool_white": 23592,
                    "violet": 7317,
                    "green": 4190,
                    "deep_red": 3768,
                    "royal": 23888,
                    "uv": 7270
                }
            }
        ],
        "response_code": 0
    }

    @staticmethod
    def power_hydra52hd_max():
        return 120000
    
    @staticmethod
    def power_hydra26hd_max():
        return 90000

    
    @staticmethod
    def power_primehd_max():
        return 48000
