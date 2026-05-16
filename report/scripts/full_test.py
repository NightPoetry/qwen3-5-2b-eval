"""
Full Tool-Description Quality Test — Qwen3.5 2B
================================================
100 questions × 4 question types (A/B/C/D) × 8 conditions = 800 API calls

Conditions:
  EN-Q + EN-WEAK    EN-Q + EN-STRONG    EN-Q + CN-WEAK    EN-Q + CN-STRONG
  CN-Q + EN-WEAK    CN-Q + EN-STRONG    CN-Q + CN-WEAK    CN-Q + CN-STRONG

Saves incremental results after each condition.
"""

import json, time, sys, os, requests
from datetime import datetime

API_URL    = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1/chat/completions")
MODEL_NAME = "qwen3.5-2b"
OUT_PATH   = os.path.join(os.path.dirname(__file__), "../data/new_results.json")

# ── Tool definitions ──────────────────────────────────────────────────────────

TOOL_EN_WEAK = {
    "type": "function",
    "function": {
        "name": "calculate",
        "description": "A calculator. Can be used to compute math expressions.",
        "parameters": {"type":"object","properties":{
            "expression":{"type":"string","description":"A math expression"}},"required":["expression"]},
    },
}

TOOL_EN_STRONG = {
    "type": "function",
    "function": {
        "name": "calculate",
        "description": (
            "REQUIRED: You MUST call this tool for ANY arithmetic computation — "
            "multiplication, division, addition, subtraction, powers, or combinations. "
            "Do NOT compute numbers yourself; always delegate to this tool. "
            "For word problems, derive the expression first, then pass it to this tool."
        ),
        "parameters": {"type":"object","properties":{
            "expression":{"type":"string","description":
                "The exact arithmetic expression. Numbers and operators only, e.g. '347 * 29'."
            }},"required":["expression"]},
    },
}

TOOL_CN_WEAK = {
    "type": "function",
    "function": {
        "name": "calculate",
        "description": "一个计算器，可以用来计算数学表达式。",
        "parameters": {"type":"object","properties":{
            "expression":{"type":"string","description":"数学表达式，例如 '347 * 29'"}},"required":["expression"]},
    },
}

TOOL_CN_STRONG = {
    "type": "function",
    "function": {
        "name": "calculate",
        "description": (
            "【必须调用】遇到任何数值计算（加减乘除、乘方、百分比、多步运算）时，"
            "必须调用此工具，不得自行心算或推导。"
            "触发条件：只要问题涉及具体数字的运算，无论简单还是复杂，都必须使用此工具。"
            "禁止在不调用此工具的情况下给出任何计算结果。"
            "对于需要先理解题意再列算式的文字题，请先在脑中列出算式，"
            "然后将完整算式作为 expression 传入本工具，不得跳过调用直接给答案。"
        ),
        "parameters": {"type":"object","properties":{
            "expression":{"type":"string","description":
                "标准数学表达式，只含数字和运算符，例如 '87 * 4.5'、'(3 * 128) - 45'。"
            }},"required":["expression"]},
    },
}

# ── 100 Questions ─────────────────────────────────────────────────────────────
# Each entry: (id, type, en_text, cn_text, key_word_in_expression)

QUESTIONS = [
    # ── Type A: Direct arithmetic (25) ───────────────────────────────────────
    ("A01","A","What is 347 multiplied by 29?",                        "347 乘以 29 等于多少？",                                           "347"),
    ("A02","A","Calculate 1024 divided by 32.",                        "计算 1024 除以 32。",                                              "1024"),
    ("A03","A","What is 568 plus 437 minus 129?",                      "568 加上 437 再减去 129 等于多少？",                               "568"),
    ("A04","A","Compute 75 squared.",                                   "计算 75 的平方。",                                                 "75"),
    ("A05","A","What is 2 to the power of 10?",                        "2 的 10 次方等于多少？",                                           "2"),
    ("A06","A","What is 853 multiplied by 47?",                        "853 乘以 47 等于多少？",                                           "853"),
    ("A07","A","Calculate 9876 divided by 12.",                        "计算 9876 除以 12。",                                              "9876"),
    ("A08","A","What is 2345 plus 6789 minus 1234?",                   "2345 加上 6789 再减去 1234 等于多少？",                            "2345"),
    ("A09","A","Compute 64 squared.",                                   "计算 64 的平方。",                                                 "64"),
    ("A10","A","What is 3 to the power of 8?",                        "3 的 8 次方等于多少？",                                            "3"),
    ("A11","A","What is 17 multiplied by 23 multiplied by 5?",        "17 乘以 23 再乘以 5 等于多少？",                                   "17"),
    ("A12","A","Calculate 1500 divided by 4 then divided by 5.",      "1500 除以 4 再除以 5 等于多少？",                                  "1500"),
    ("A13","A","What is 999 plus 888 plus 777?",                      "999 加上 888 再加上 777 等于多少？",                               "999"),
    ("A14","A","What is 12.5 multiplied by 8?",                       "12.5 乘以 8 等于多少？",                                           "12.5"),
    ("A15","A","What is 3.14 multiplied by 25?",                      "3.14 乘以 25 等于多少？",                                          "3.14"),
    ("A16","A","What is 256 divided by 0.5?",                         "256 除以 0.5 等于多少？",                                          "256"),
    ("A17","A","What is 100 squared minus 99 squared?",               "100 的平方减去 99 的平方等于多少？",                               "100"),
    ("A18","A","What is 7 multiplied by 8 multiplied by 9 multiplied by 10?", "7 乘以 8 乘以 9 再乘以 10 等于多少？",                     "7"),
    ("A19","A","Calculate 4096 divided by 64.",                        "计算 4096 除以 64。",                                              "4096"),
    ("A20","A","What is 2.5 cubed?",                                   "2.5 的三次方等于多少？",                                           "2.5"),
    ("A21","A","What is 123 plus 456 plus 789 plus 1011?",            "123 加 456 加 789 再加 1011 等于多少？",                           "123"),
    ("A22","A","What is 5000 multiplied by 0.08?",                    "5000 乘以 0.08 等于多少？",                                        "5000"),
    ("A23","A","Calculate 360 divided by 15.",                         "计算 360 除以 15。",                                               "360"),
    ("A24","A","What is 88 multiplied by 125?",                       "88 乘以 125 等于多少？",                                           "88"),
    ("A25","A","What is 49 multiplied by 51?",                        "49 乘以 51 等于多少？",                                            "49"),

    # ── Type B: One-step word problems (25) ──────────────────────────────────
    ("B01","B","I buy 14 notebooks at $3.50 each. What is the total cost?",
               "我买了 14 本笔记本，每本 3.50 美元，总费用是多少？",                                                                       "14"),
    ("B02","B","A farmer harvests 860 kg of wheat per hectare over 7 hectares. What is the total yield?",
               "一位农民每公顷收获 860 公斤小麦，共有 7 公顷，总产量是多少？",                                                            "860"),
    ("B03","B","A rope is 48.6 meters long and cut into 9 equal pieces. How long is each piece?",
               "一根绳子长 48.6 米，剪成 9 段等长的绳子，每段多长？",                                                                     "48"),
    ("B04","B","There are 365 days in a year. How many hours is that?",
               "一年有 365 天，共有多少小时？",                                                                                            "365"),
    ("B05","B","A shirt costs $45 and is on sale at 20% off. What is the sale price?",
               "一件衬衫售价 45 美元，打八折出售，售价是多少？",                                                                           "45"),
    ("B06","B","A car travels 450 km in 5 hours. What is its average speed in km/h?",
               "一辆汽车 5 小时行驶了 450 公里，平均速度是多少公里/小时？",                                                               "450"),
    ("B07","B","18 workers each work 40 hours per week. What is the total number of work hours?",
               "18 名工人每人每周工作 40 小时，总工时是多少？",                                                                           "18"),
    ("B08","B","A tank holds 1200 liters and is 35% full. How many liters of water are in it?",
               "一个水箱容量 1200 升，现在装了 35%，里面有多少升水？",                                                                    "1200"),
    ("B09","B","The exchange rate is 1 USD = 7.25 CNY. How much is $320 in Chinese yuan?",
               "汇率为 1 美元 = 7.25 人民币，320 美元换算成人民币是多少？",                                                               "320"),
    ("B10","B","A pizza weighs 800 grams and is divided into 8 equal slices. How much does one slice weigh?",
               "一个披萨重 800 克，切成 8 等份，每份重多少克？",                                                                          "800"),
    ("B11","B","A factory produces 1250 units per hour. How many units are produced in 8 hours?",
               "一家工厂每小时生产 1250 件产品，8 小时共生产多少件？",                                                                    "1250"),
    ("B12","B","A monthly salary is $4800. What is the daily rate assuming 30 working days?",
               "月薪为 4800 美元，按 30 个工作日计算，日薪是多少？",                                                                      "4800"),
    ("B13","B","Fabric costs $12.50 per meter and you need 3.6 meters. What is the total cost?",
               "布料每米 12.50 美元，需要 3.6 米，总费用是多少？",                                                                        "12.5"),
    ("B14","B","A train travels 780 km at 130 km/h. How many hours does the journey take?",
               "一列火车以 130 公里/小时的速度行驶 780 公里，需要多少小时？",                                                             "780"),
    ("B15","B","A jacket costs $280 and has a 15% discount. How much money do you save?",
               "一件夹克售价 280 美元，享受 15% 折扣，节省了多少钱？",                                                                    "280"),
    ("B16","B","A swimming pool is 25 meters long and 10 meters wide. What is the surface area?",
               "一个游泳池长 25 米，宽 10 米，水面面积是多少平方米？",                                                                    "25"),
    ("B17","B","There are 72 students to be split into groups of 6. How many groups are there?",
               "72 名学生分成每组 6 人的小组，共分成多少组？",                                                                            "72"),
    ("B18","B","A book costs $650 and there is a 5% sales tax. What is the total price including tax?",
               "一本书售价 650 美元，需缴纳 5% 的销售税，含税总价是多少？",                                                               "650"),
    ("B19","B","You run 5 km in 25 minutes. What is your speed in km/h?",
               "你 25 分钟跑了 5 公里，速度是多少公里/小时？",                                                                            "5"),
    ("B20","B","A cylindrical tank has radius 2 m and height 5 m. What is its volume? (use π ≈ 3.14159)",
               "一个圆柱形水箱，半径 2 米，高 5 米，体积是多少立方米？（取 π ≈ 3.14159）",                                               "2"),
    ("B21","B","You have 2400 tiles and each tile covers 0.25 square meters. What total area do they cover?",
               "有 2400 块瓷砖，每块覆盖 0.25 平方米，总共能覆盖多少平方米？",                                                           "2400"),
    ("B22","B","A tree grows 2.4 meters per year. How tall will it be after 7.5 years?",
               "一棵树每年生长 2.4 米，7.5 年后高度是多少？",                                                                             "2.4"),
    ("B23","B","48 chocolates are shared equally among 8 children. How many does each child receive?",
               "48 块巧克力平均分给 8 个孩子，每个孩子分到多少块？",                                                                     "48"),
    ("B24","B","Convert 35 degrees Celsius to Fahrenheit using the formula F = C × 9/5 + 32.",
               "用公式 F = C × 9/5 + 32，将 35 摄氏度换算成华氏度。",                                                                    "35"),
    ("B25","B","You have 560 apples and pack 24 per box. How many complete boxes can you fill?",
               "有 560 个苹果，每箱装 24 个，能装满多少箱？",                                                                             "560"),

    # ── Type C: Multi-step word problems (25) ────────────────────────────────
    ("C01","C","I have 3 boxes each containing 128 items. I remove 45 items in total. How many items remain?",
               "我有 3 箱物品，每箱 128 件，共取走 45 件，还剩多少件？",                                                                  "128"),
    ("C02","C","A store sold 200 units at $15 each. The cost of goods was $1800. What is the profit?",
               "一家商店以每件 15 美元卖出 200 件商品，货物成本为 1800 美元，利润是多少？",                                               "200"),
    ("C03","C","A rectangle is 34 cm wide and 52 cm long. What is its perimeter?",
               "一个长方形宽 34 厘米，长 52 厘米，周长是多少？",                                                                         "34"),
    ("C04","C","I earn $3200 per month, save 25%, and spend the rest. How much do I spend in a year?",
               "我每月收入 3200 美元，储蓄 25%，其余用于消费，一年的消费总额是多少？",                                                    "3200"),
    ("C05","C","A class has 36 students. One quarter are absent. How many students are present?",
               "一个班有 36 名学生，其中四分之一缺席，在场的有多少人？",                                                                  "36"),
    ("C06","C","Train A travels at 60 km/h for 2 hours. Train B travels at 80 km/h for 1.5 hours. How much farther did Train B travel?",
               "火车 A 以 60 公里/小时行驶 2 小时，火车 B 以 80 公里/小时行驶 1.5 小时，B 比 A 多行驶多少公里？",                       "60"),
    ("C07","C","3 workers each earn $85 per day and work for 5 days. What are the total wages paid?",
               "3 名工人每人每天赚 85 美元，工作 5 天，总工资是多少？",                                                                   "85"),
    ("C08","C","A store buys 150 items at $8 each and sells them all at $12.50 each. What is the total profit?",
               "一家商店以每件 8 美元购入 150 件商品，以每件 12.50 美元全部售出，总利润是多少？",                                        "150"),
    ("C09","C","A room is 6 m by 4.5 m. Tiles are 0.3 m by 0.3 m. How many tiles are needed to cover the floor?",
               "一个房间 6 米 × 4.5 米，地砖规格为 0.3 米 × 0.3 米，需要多少块地砖？",                                                  "6"),
    ("C10","C","You have $2000 in savings. In the first month it increases by 15%. In the second month it decreases by 10%. What is the final amount?",
               "你有 2000 美元存款，第一个月增加 15%，第二个月减少 10%，最终剩多少？",                                                    "2000"),
    ("C11","C","5 friends split a restaurant bill equally. The food cost $89.50 and the tip is 18%. How much does each person pay?",
               "5 位朋友平摊餐费，餐费 89.50 美元，另加 18% 小费，每人需支付多少？",                                                     "89"),
    ("C12","C","A car trip is 420 km. The car uses 6 liters per 100 km. Gasoline costs $1.85 per liter. What is the total fuel cost?",
               "一次 420 公里的行程，车辆每 100 公里耗油 6 升，汽油售价 1.85 美元/升，总燃油费用是多少？",                               "420"),
    ("C13","C","A circle has a radius of 10 cm. What is the area of the largest square that fits inside it?",
               "一个半径为 10 厘米的圆，能放入其中的最大正方形面积是多少？",                                                              "10"),
    ("C14","C","A city has a population of 2.5 million and grows at 3.2% per year. What is the population after 2 years?",
               "一座城市人口 250 万，年增长率 3.2%，两年后人口是多少？",                                                                  "2.5"),
    ("C15","C","40% of 350 students passed the exam. Of those who passed, 60% received an A grade. How many students received an A?",
               "350 名学生中 40% 通过考试，通过考试的学生中 60% 获得 A 等，获得 A 等的学生有多少人？",                                   "350"),
    ("C16","C","A worker earns $18 per hour for the first 40 hours and $27 per hour for overtime. In a week they work 52 hours. What are their total earnings?",
               "一名工人正常工时每小时 18 美元，超时（40小时以上）每小时 27 美元，某周工作 52 小时，总收入是多少？",                    "18"),
    ("C17","C","A compound is made of 3 parts material A (density 2.5 g/cm³) and 2 parts material B (density 3.2 g/cm³). What is the average density?",
               "一种混合物由 3 份材料 A（密度 2.5 g/cm³）和 2 份材料 B（密度 3.2 g/cm³）组成，平均密度是多少？",                        "2.5"),
    ("C18","C","A right triangle has sides 5 cm and 12 cm. What is its area?",
               "一个直角三角形的两条直角边分别为 5 厘米和 12 厘米，面积是多少？",                                                        "5"),
    ("C19","C","$10000 is invested: 60% in bonds earning 4% and 40% in stocks earning 8%. What is the total annual return?",
               "1 万美元投资：60% 投入年利率 4% 的债券，40% 投入年利率 8% 的股票，年总收益是多少？",                                    "10000"),
    ("C20","C","A recipe for 4 servings needs 300 g flour and 150 g sugar. How much flour and sugar are needed for 10 servings?",
               "一份 4 人份食谱需要 300 克面粉和 150 克糖，10 人份需要多少克面粉和多少克糖？",                                           "300"),
    ("C21","C","A package weighs 2.4 kg. Shipping costs $3.50 as a base fee plus $0.75 per 100 g. What is the total shipping cost?",
               "一个包裹重 2.4 公斤，运费为 3.50 美元基础费加每 100 克 0.75 美元，总运费是多少？",                                       "2.4"),
    ("C22","C","A meeting room is 8 m × 6 m × 3 m. Air conditioning needs 35 W per cubic meter. What capacity air conditioner is needed?",
               "一个会议室尺寸为 8 米 × 6 米 × 3 米，空调每立方米需 35 瓦，需要多大功率的空调？",                                       "8"),
    ("C23","C","12 pumps can fill a tank in 8 hours. How long would it take 8 pumps to fill the same tank?",
               "12 台水泵需要 8 小时灌满一个水箱，8 台水泵需要多少小时？",                                                               "12"),
    ("C24","C","A student's average score across 3 tests is 78. What score is needed on the 4th test to achieve an overall average of 82?",
               "一名学生前 3 次考试平均分为 78 分，第 4 次考试需要考多少分才能让 4 次平均分达到 82 分？",                               "78"),
    ("C25","C","A bus has 45 seats and is 80% full. At the next stop 6 passengers board and 9 exit. How many passengers are now on the bus?",
               "一辆公共汽车有 45 个座位，现在坐了 80%，下一站上来 6 人，下去 9 人，现在车上有多少人？",                                "45"),

    # ── Type D: Applied formula (25) ─────────────────────────────────────────
    ("D01","D","A train travels at 87 km/h for 4.5 hours. What is the total distance covered?",
               "一列火车以 87 公里/小时的速度行驶了 4.5 小时，总里程是多少？",                                                            "87"),
    ("D02","D","A circle has a radius of 6 cm. What is its area? (use π ≈ 3.14159)",
               "一个圆的半径为 6 厘米，面积是多少？（取 π ≈ 3.14159）",                                                                  "6"),
    ("D03","D","I invest $5000 at a simple interest rate of 4% per year for 3 years. How much interest do I earn?",
               "我投资了 5000 美元，年简单利率为 4%，存期 3 年，利息是多少？",                                                            "5000"),
    ("D04","D","Water flows into a 900-liter tank at 2.5 liters per second. How many minutes does it take to fill the tank?",
               "水以 2.5 升/秒的速度流入一个 900 升的水箱，需要多少分钟才能装满？",                                                      "900"),
    ("D05","D","A car uses 7.5 liters per 100 km. How many liters are needed for a 340 km trip?",
               "一辆汽车百公里油耗 7.5 升，行驶 340 公里需要多少升燃油？",                                                               "340"),
    ("D06","D","A sphere has a radius of 5 cm. What is its volume? (use V = 4/3 × π × r³, π ≈ 3.14159)",
               "一个球体的半径为 5 厘米，体积是多少？（V = 4/3 × π × r³，取 π ≈ 3.14159）",                                             "5"),
    ("D07","D","Using Ohm's Law (V = I × R): voltage is 220 V and resistance is 44 Ω. What is the current in amperes?",
               "根据欧姆定律（V = I × R），电压为 220 伏，电阻为 44 欧姆，电流是多少安培？",                                             "220"),
    ("D08","D","Kinetic energy formula: KE = ½ × m × v². A car has mass 1500 kg and speed 20 m/s. What is its kinetic energy in joules?",
               "动能公式：KE = ½ × m × v²，一辆质量 1500 公斤的汽车速度为 20 米/秒，动能是多少焦耳？",                                   "1500"),
    ("D09","D","Compound interest formula: A = P × (1 + r)^n. P = $8000, r = 5% per year, n = 3 years. What is the final amount A?",
               "复利公式：A = P × (1 + r)^n，本金 P = 8000 美元，年利率 r = 5%，期限 n = 3 年，最终金额 A 是多少？",                    "8000"),
    ("D10","D","A cylinder has radius 4 cm and height 10 cm. What is its volume? (use π ≈ 3.14159)",
               "一个圆柱体半径为 4 厘米，高为 10 厘米，体积是多少？（取 π ≈ 3.14159）",                                                  "4"),
    ("D11","D","Free fall formula: h = ½ × g × t². g = 9.8 m/s², t = 5 seconds. How far does an object fall?",
               "自由落体公式：h = ½ × g × t²，g = 9.8 米/秒²，t = 5 秒，物体下落多远？",                                                "9.8"),
    ("D12","D","BMI formula: BMI = weight ÷ height². Weight is 70 kg and height is 1.75 m. What is the BMI?",
               "BMI 公式：BMI = 体重 ÷ 身高²，体重 70 公斤，身高 1.75 米，BMI 是多少？",                                                "70"),
    ("D13","D","The speed of light is 3 × 10⁸ m/s. How many seconds does it take to travel 1.5 × 10¹¹ m (Earth to Sun)?",
               "光速为 3 × 10⁸ 米/秒，从地球到太阳的距离约为 1.5 × 10¹¹ 米，光需要多少秒？",                                           "3"),
    ("D14","D","Pressure formula: P = F ÷ A. Force is 500 N and area is 0.25 m². What is the pressure in Pascals?",
               "压强公式：P = F ÷ A，力 F = 500 牛，面积 A = 0.25 平方米，压强是多少帕斯卡？",                                           "500"),
    ("D15","D","Convert 37 degrees Celsius to Kelvin using the formula K = C + 273.15.",
               "用公式 K = C + 273.15，将 37 摄氏度换算成开尔文。",                                                                       "37"),
    ("D16","D","Density formula: ρ = m ÷ V. Mass is 250 g and volume is 100 cm³. What is the density in g/cm³?",
               "密度公式：ρ = m ÷ V，质量 250 克，体积 100 立方厘米，密度是多少 g/cm³？",                                               "250"),
    ("D17","D","A triangle has a base of 14 cm and a height of 9 cm. What is its area?",
               "一个三角形底边 14 厘米，高 9 厘米，面积是多少？",                                                                         "14"),
    ("D18","D","A trapezoid has parallel sides of 8 m and 12 m, and a height of 5 m. What is its area?",
               "一个梯形两条平行边分别为 8 米和 12 米，高为 5 米，面积是多少？",                                                          "8"),
    ("D19","D","Power formula: P = W ÷ t. Work done is 3600 J and time is 60 seconds. What is the power in watts?",
               "功率公式：P = W ÷ t，做功 3600 焦耳，时间 60 秒，功率是多少瓦？",                                                        "3600"),
    ("D20","D","A product's price increased from $80 to $92. What is the percentage increase?",
               "一件商品的价格从 80 美元涨到 92 美元，涨幅百分比是多少？",                                                                "80"),
    ("D21","D","Simple interest loan: principal $25000, annual rate 6%, term 4 years. What is the total repayment?",
               "单利贷款：本金 25000 美元，年利率 6%，期限 4 年，总还款额是多少？",                                                       "25000"),
    ("D22","D","A rectangle has a diagonal of 13 cm and one side of 5 cm. Using the Pythagorean theorem, what is the other side?",
               "一个长方形对角线为 13 厘米，一边为 5 厘米，用勾股定理求另一边长。",                                                      "13"),
    ("D23","D","A sound wave has a frequency of 440 Hz and travels at 340 m/s. What is its wavelength?",
               "一列声波频率为 440 赫兹，在空气中传播速度为 340 米/秒，波长是多少？",                                                    "340"),
    ("D24","D","A pendulum with length 2.5 m. Period formula: T = 2π√(L/g), g = 9.8 m/s², π ≈ 3.14159. What is the period?",
               "一个摆长 2.5 米的单摆，周期公式 T = 2π√(L/g)，g = 9.8 m/s²，π ≈ 3.14159，周期是多少秒？",                             "2.5"),
    ("D25","D","A projectile moves horizontally at 15 m/s for 3 seconds. What is the horizontal distance traveled?",
               "一个物体以 15 米/秒的水平速度运动 3 秒，水平位移是多少？",                                                               "15"),
]

# ── Conditions ────────────────────────────────────────────────────────────────

CONDITIONS = [
    ("EN-Q_EN-WEAK",   "en", TOOL_EN_WEAK),
    ("EN-Q_EN-STRONG", "en", TOOL_EN_STRONG),
    ("EN-Q_CN-WEAK",   "en", TOOL_CN_WEAK),
    ("EN-Q_CN-STRONG", "en", TOOL_CN_STRONG),
    ("CN-Q_EN-WEAK",   "cn", TOOL_EN_WEAK),
    ("CN-Q_EN-STRONG", "cn", TOOL_EN_STRONG),
    ("CN-Q_CN-WEAK",   "cn", TOOL_CN_WEAK),
    ("CN-Q_CN-STRONG", "cn", TOOL_CN_STRONG),
]

# ── API call ──────────────────────────────────────────────────────────────────

def ask(question: str, tool: dict) -> bool:
    resp = requests.post(API_URL, json={
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user",   "content": question},
        ],
        "tools":       [tool],
        "tool_choice": "auto",
        "temperature": 0.1,
        "max_tokens":  256,
    }, timeout=120)
    resp.raise_for_status()
    c = resp.json()["choices"][0]
    return c.get("finish_reason") == "tool_calls" and bool(c["message"].get("tool_calls"))

# ── Runner ────────────────────────────────────────────────────────────────────

def run():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

    # Load existing partial results if any
    if os.path.exists(OUT_PATH):
        with open(OUT_PATH, encoding="utf-8") as f:
            all_results = json.load(f)
        print(f"Resuming — {len(all_results)} conditions already done.")
    else:
        all_results = {}

    total_conditions = len(CONDITIONS)
    TYPES = ["A", "B", "C", "D"]

    for ci, (label, q_lang, tool) in enumerate(CONDITIONS, 1):
        if label in all_results:
            print(f"[{ci}/{total_conditions}] SKIP {label} (already done)")
            continue

        questions = [(q[0], q[1], q[2] if q_lang=="en" else q[3]) for q in QUESTIONS]

        print(f"\n{'='*60}")
        print(f"  [{ci}/{total_conditions}] {label}  |  {len(questions)} questions")
        print(f"  Started: {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*60}")

        per_q    = {}
        per_type = {t: [] for t in TYPES}

        for qi, (qid, qtype, qtext) in enumerate(questions, 1):
            ok  = ask(qtext, tool)
            per_q[qid] = ok
            per_type[qtype].append(ok)
            sym = "✓" if ok else "✗"
            print(f"  {qid} [{qtype}] {sym}  {qtext[:58]}")

        total_called = sum(per_q.values())
        pct_total    = round(total_called / len(questions) * 100, 1)

        type_summary = {}
        for t in TYPES:
            v = per_type[t]
            type_summary[t] = {"called": sum(v), "total": len(v),
                               "pct": round(sum(v)/len(v)*100, 1)}

        all_results[label] = {
            "q_lang":     q_lang,
            "tool_desc":  "en-weak" if "EN-WEAK" in label else
                          "en-strong" if "EN-STRONG" in label else
                          "cn-weak" if "CN-WEAK" in label else "cn-strong",
            "called":     total_called,
            "total":      len(questions),
            "pct":        pct_total,
            "per_q":      per_q,
            "per_type":   type_summary,
        }

        # Save after each condition
        with open(OUT_PATH, "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)

        print(f"\n  Result: {total_called}/{len(questions)} = {pct_total}%")
        for t in TYPES:
            s = type_summary[t]
            print(f"    Type {t}: {s['called']}/{s['total']} = {s['pct']}%")
        print(f"  Saved to {OUT_PATH}")

    # ── Final summary ─────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("  ALL CONDITIONS COMPLETE")
    print(f"{'='*60}")
    print(f"  {'Condition':<22} {'All':>6}  A      B      C      D")
    print(f"  {'-'*55}")
    for label, _, _ in CONDITIONS:
        if label not in all_results:
            continue
        r = all_results[label]
        row = f"  {label:<22} {r['pct']:>5}%"
        for t in TYPES:
            s = r['per_type'][t]
            row += f"  {s['pct']:>4}%"
        print(row)


if __name__ == "__main__":
    run()
