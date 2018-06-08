
class TestData:

    @staticmethod
    def identity_1(): 
        
        return {
        "serial_number": "D8976003AAAA",
        "parent": "",
        "firmware": "2.0.0",
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
    def identity_2(): 
        
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
    def set_colors_max_hd_primeHD(): 
        return {
        "deep_red": 100,
        "uv": 100,
        "violet": 100,
        "cool_white": 76,
        "green": 100,
        "blue": 108,
        "royal": 117
    }
    
    @staticmethod
    def set_colors_max_hd_hydra26HD(): 
        return {
        "deep_red": 4,
        "uv": 116,
        "violet": 116,
        "cool_white": 137,
        "green": 5,
        "blue": 79,
        "royal": 103
    }
    
    @staticmethod
    def set_colors_hd_exceeded(): 
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
    def set_result_colors_3(): 
        return {
        "deep_red": 0,
        "uv": 420,
        "violet": 1273,
        "cool_white": 0,
        "green": 0,
        "blue": 0,
        "royal": 1429
    }

    @staticmethod
    def set_result_colors_max_hd_primeHD(): 
        return {
        "deep_red": 1000,
        "uv": 1000,
        "violet": 1000,
        "cool_white": 760,
        "green": 1000,
        "blue": 1727,
        "royal": 1771
    }

    @staticmethod
    def set_result_colors_max_hd_hydra26HD(): 
        return {
        "deep_red": 40,
        "uv": 1889,
        "violet": 1875,
        "cool_white": 760,
        "green": 1000,
        "blue": 1727,
        "royal": 1771
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
    def power_primehd():
        return {
        "devices": [
            {
                "serial_number": "D89760043242",
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
    def power_hydra26hd_hd():
        return {
            "blue": 23137,
            "cool_white": 32272,
            "violet": 8654,
            "green": 8769,
            "deep_red": 6950,
            "royal": 33350,
            "uv": 8577
        }


    @staticmethod
    def power_primehd_hd():
        return {
                    "royal": 16400,
                    "cool_white": 15400,
                    "green": 4100,
                    "violet": 4000,
                    "uv": 4630,
                    "blue": 9670,
                    "deep_red": 3380
                }


    @staticmethod
    def power_hydra26hd_norm():
        return {
            "blue": 19975,
            "cool_white": 23592,
            "violet": 7317,
            "green": 4190,
            "deep_red": 3768,
            "royal": 23888,
            "uv": 7270
        }


    @staticmethod
    def power_primehd_norm():
        return {
                    "royal": 13440,
                    "cool_white": 12756,
                    "green": 3132,
                    "violet": 3458,
                    "uv": 3876,
                    "blue": 8712,
                    "deep_red": 2626
                }

    
    @staticmethod
    def power_hydra26hd_max():
        return 90000

    
    @staticmethod
    def power_primehd_max():
        return 48000



