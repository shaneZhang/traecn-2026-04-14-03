import pandas as pd
import random
from datetime import datetime, timedelta


def generate_sample_data(num_records=500):
    random.seed(42)
    
    genders = ['男', '女']
    educations = ['大专', '本科', '硕士', '博士']
    industries = ['互联网', '金融', '房地产', '制造业', '教育', '医疗', '咨询', '电商']
    position_types = ['技术', '产品', '设计', '运营', '市场', '销售', '人事', '财务', '行政']
    levels = ['初级', '中级', '高级', '专家', '经理', '总监']
    company_sizes = ['小型(50人以下)', '中型(50-200人)', '大型(200-1000人)', '超大型(1000人以上)']
    
    data = []
    
    for i in range(num_records):
        gender = random.choice(genders)
        education = random.choice(educations)
        industry = random.choice(industries)
        position = random.choice(position_types)
        level = random.choice(levels)
        company_size = random.choice(company_sizes)
        
        age = random.randint(22, 55)
        work_years = max(0, age - 22 - random.randint(0, 3))
        
        base = random.randint(4000, 25000)
        
        if level == '初级':
            multiplier = random.uniform(1.0, 1.3)
        elif level == '中级':
            multiplier = random.uniform(1.3, 1.8)
        elif level == '高级':
            multiplier = random.uniform(1.8, 2.5)
        elif level == '专家':
            multiplier = random.uniform(2.5, 3.5)
        elif level == '经理':
            multiplier = random.uniform(2.0, 3.0)
        else:
            multiplier = random.uniform(2.5, 4.0)
        
        base_salary = int(base * multiplier)
        
        if industry == '互联网':
            base_salary = int(base_salary * 1.2)
        elif industry == '金融':
            base_salary = int(base_salary * 1.15)
        
        if education == '硕士':
            base_salary = int(base_salary * 1.1)
        elif education == '博士':
            base_salary = int(base_salary * 1.2)
        
        performance_bonus = int(base_salary * random.uniform(0, 0.5))
        allowance = random.randint(500, 3000)
        
        pre_tax = base_salary + performance_bonus + allowance
        tax = pre_tax * random.uniform(0.1, 0.25)
        post_tax = pre_tax - tax
        
        join_year = random.randint(2015, 2024)
        
        data.append({
            '姓名': f'员工{i+1:04d}',
            '性别': gender,
            '年龄': age,
            '学历': education,
            '工作年限': work_years,
            '所在行业': industry,
            '岗位类型': position,
            '职级': level,
            '基本工资': base_salary,
            '绩效奖金': performance_bonus,
            '补贴总和': allowance,
            '税前薪资': pre_tax,
            '税后薪资': post_tax,
            '所属企业规模': company_size,
            '入职年份': join_year
        })
    
    df = pd.DataFrame(data)
    return df


if __name__ == '__main__':
    print('正在生成示例数据...')
    
    df = generate_sample_data(500)
    
    output_path = 'sample_data/薪资数据样本.xlsx'
    df.to_excel(output_path, index=False)
    
    print(f'示例数据已生成: {output_path}')
    print(f'共 {len(df)} 条记录')
    print(f'字段: {list(df.columns)}')
    print(f'\n数据预览:')
    print(df.head(10))
    print(f'\n薪资统计:')
    print(df['税前薪资'].describe())
