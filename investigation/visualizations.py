import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def create_visualizations():
    # 1. Setup & Data Loading
    file_path = 'data.xlsx'
    output_dir = 'visualizations'
    os.makedirs(output_dir, exist_ok=True)
    
    # Handle potential sheet naming differences
    xls = pd.ExcelFile(file_path)
    sheet_name = 'Transactions' if 'Transactions' in xls.sheet_names else xls.sheet_names[0]
    df = pd.read_excel(xls, sheet_name=sheet_name)
    
    # 2. Data Cleaning & Feature Engineering
    df['Transaction Date'] = pd.to_datetime(df['Transaction Date'])
    df['Date'] = df['Transaction Date'].dt.date
    df['Day_Name'] = df['Transaction Date'].dt.day_name()
    df['Is_Weekend'] = df['Transaction Date'].dt.dayofweek >= 5
    df['Week_Number'] = df['Transaction Date'].dt.isocalendar().week
    
    income_df = df[df['Amount'] > 0].copy()
    expense_df = df[df['Amount'] < 0].copy()
    expense_df['Amount_Abs'] = expense_df['Amount'].abs()
    
    # Define Fixed vs Variable
    fixed_cats = ['Fixed Commitments', 'Debit Order', 'Bank Fees', 'Investments / Transfers']
    expense_df['Exp_Type'] = expense_df['Category'].apply(lambda x: 'Fixed' if x in fixed_cats else 'Variable')
    
    # Global plot styling
    sns.set_theme(style="whitegrid")
    
    # --- VISUALIZATION 1: Running Balance Trajectory ---
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df, x='Transaction Date', y='Running Balance', color='dodgerblue', linewidth=2)
    plt.axhline(0, color='red', linestyle='--', linewidth=1.5)
    plt.title('1. Running Balance Trajectory Over Time', fontsize=14)
    plt.ylabel('Balance (ZAR)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/01_running_balance.png')
    plt.close()

    # --- VISUALIZATION 2: Cumulative Fixed vs Variable Spend ---
    exp_sorted = expense_df.sort_values('Date')
    fixed_cum = exp_sorted[exp_sorted['Exp_Type'] == 'Fixed'].groupby('Date')['Amount_Abs'].sum().cumsum()
    var_cum = exp_sorted[exp_sorted['Exp_Type'] == 'Variable'].groupby('Date')['Amount_Abs'].sum().cumsum()
    
    plt.figure(figsize=(12, 6))
    plt.plot(fixed_cum.index, fixed_cum.values, label='Cumulative Fixed', color='purple', linewidth=2)
    plt.plot(var_cum.index, var_cum.values, label='Cumulative Variable', color='orange', linewidth=2)
    plt.title('2. Cumulative Spending: Fixed vs Variable', fontsize=14)
    plt.ylabel('Amount (ZAR)')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/02_cumulative_spending.png')
    plt.close()

    # --- VISUALIZATION 3: Total Income vs Total Expense ---
    plt.figure(figsize=(8, 6))
    totals = [income_df['Amount'].sum(), expense_df['Amount_Abs'].sum()]
    sns.barplot(x=['Total Income', 'Total Expense'], y=totals, palette=['mediumseagreen', 'crimson'])
    plt.title('3. Overall Cashflow Summary', fontsize=14)
    plt.ylabel('Amount (ZAR)')
    for i, v in enumerate(totals):
        plt.text(i, v + 500, f'R {v:,.2f}', ha='center', fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/03_income_vs_expense.png')
    plt.close()

    # --- VISUALIZATION 4: Fixed vs Variable Proportion (Donut Chart) ---
    plt.figure(figsize=(8, 8))
    type_totals = expense_df.groupby('Exp_Type')['Amount_Abs'].sum()
    plt.pie(type_totals, labels=type_totals.index, autopct='%1.1f%%', startangle=90, colors=['purple', 'orange'], wedgeprops={'width': 0.4})
    plt.title('4. Fixed vs Variable Spending Proportion', fontsize=14)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/04_fixed_vs_variable_donut.png')
    plt.close()

    # --- VISUALIZATION 5: Category Spend Breakdown (Horizontal Bar) ---
    cat_totals = expense_df.groupby('Category')['Amount_Abs'].sum().sort_values(ascending=False)
    plt.figure(figsize=(12, 8))
    sns.barplot(x=cat_totals.values, y=cat_totals.index, palette='viridis')
    plt.title('5. Total Spend by Category', fontsize=14)
    plt.xlabel('Amount (ZAR)')
    for i, v in enumerate(cat_totals.values):
        plt.text(v + 100, i, f'R {v:,.0f}', va='center')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/05_category_breakdown_bar.png')
    plt.close()

    # --- VISUALIZATION 6: Category Spend Percentages (Donut Chart) ---
    plt.figure(figsize=(10, 10))
    plt.pie(cat_totals, labels=cat_totals.index, autopct='%1.1f%%', startangle=140, pctdistance=0.85, wedgeprops={'width': 0.4})
    plt.title('6. Percentage Breakdown of Spend by Category', fontsize=14)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/06_category_breakdown_donut.png')
    plt.close()

    # --- VISUALIZATION 7: Weekday vs Weekend Average Daily Spend ---
    day_stats = expense_df.groupby('Is_Weekend')['Amount_Abs'].sum()
    days_count = df.groupby('Is_Weekend')['Date'].nunique()
    avg_spend = day_stats / days_count
    
    plt.figure(figsize=(8, 6))
    sns.barplot(x=['Weekday', 'Weekend'], y=avg_spend.values, palette=['skyblue', 'salmon'])
    plt.title('7. Average Daily Spend: Weekday vs Weekend', fontsize=14)
    plt.ylabel('Average Spend (ZAR)')
    for i, v in enumerate(avg_spend.values):
        plt.text(i, v + 50, f'R {v:,.2f}', ha='center', fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/07_weekday_vs_weekend.png')
    plt.close()

    # --- VISUALIZATION 8: Total Spend by Day of the Week ---
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dow_totals = expense_df.groupby('Day_Name')['Amount_Abs'].sum().reindex(days_order)
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x=dow_totals.index, y=dow_totals.values, palette='magma')
    plt.title('8. Total Spend by Day of the Week', fontsize=14)
    plt.ylabel('Amount (ZAR)')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/08_day_of_week_spend.png')
    plt.close()

    # --- VISUALIZATION 9: Weekly Spend Breakdown ---
    week_totals = expense_df.groupby('Week_Number')['Amount_Abs'].sum()
    plt.figure(figsize=(10, 6))
    sns.barplot(x=[f'Week {w}' for w in week_totals.index], y=week_totals.values, palette='coolwarm')
    plt.title('9. Total Spend per Week', fontsize=14)
    plt.ylabel('Amount (ZAR)')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/09_weekly_spend.png')
    plt.close()

    # --- VISUALIZATION 10: Top 10 Largest Single Transactions ---
    top_10 = expense_df.nlargest(10, 'Amount_Abs')
    plt.figure(figsize=(12, 6))
    sns.barplot(x='Amount_Abs', y='Narrative', data=top_10, palette='Reds_r')
    plt.title('10. Top 10 Largest Individual Expenses', fontsize=14)
    plt.xlabel('Amount (ZAR)')
    plt.ylabel('')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/10_top_10_transactions.png')
    plt.close()

    # --- VISUALIZATION 11: Transaction Volume by Category (Count) ---
    cat_counts = expense_df['Category'].value_counts()
    plt.figure(figsize=(12, 6))
    sns.barplot(x=cat_counts.values, y=cat_counts.index, palette='crest')
    plt.title('11. Frequency of Transactions by Category (Count)', fontsize=14)
    plt.xlabel('Number of Transactions')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/11_transaction_frequency.png')
    plt.close()

    # --- VISUALIZATION 12: Daily Expense Heatmap/Timeline (Scatter) ---
    plt.figure(figsize=(12, 6))
    sns.scatterplot(data=expense_df, x='Transaction Date', y='Amount_Abs', hue='Exp_Type', size='Amount_Abs', sizes=(50, 500), alpha=0.7)
    plt.title('12. Daily Expense Timeline (Size = Transaction Amount)', fontsize=14)
    plt.ylabel('Amount (ZAR)')
    plt.xticks(rotation=45)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/12_daily_expense_timeline.png')
    plt.close()

    # --- VISUALIZATION 13: Expense Distribution (Histogram) ---
    plt.figure(figsize=(10, 6))
    sns.histplot(expense_df['Amount_Abs'], bins=20, kde=True, color='teal')
    plt.title('13. Distribution of Expense Amounts', fontsize=14)
    plt.xlabel('Transaction Amount (ZAR)')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/13_expense_distribution.png')
    plt.close()

    # --- VISUALIZATION 14: Daily Total Spend Overlay (Bar) ---
    daily_spend = expense_df.groupby('Date')['Amount_Abs'].sum()
    plt.figure(figsize=(14, 6))
    sns.barplot(x=daily_spend.index.astype(str), y=daily_spend.values, color='coral')
    plt.title('14. Total Daily Spend', fontsize=14)
    plt.xticks(rotation=90)
    plt.ylabel('Amount (ZAR)')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/14_daily_total_spend.png')
    plt.close()

    # --- VISUALIZATION 15: Income vs Expense Timeline (Stem/Scatter Plot) ---
    plt.figure(figsize=(14, 6))
    plt.stem(income_df['Transaction Date'], income_df['Amount'], linefmt='g-', markerfmt='go', basefmt='k-', label='Income')
    plt.stem(expense_df['Transaction Date'], expense_df['Amount'], linefmt='r-', markerfmt='ro', basefmt='k-', label='Expense')
    plt.title('15. Money Inflow vs Outflow Timeline', fontsize=14)
    plt.ylabel('Amount (ZAR)')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/15_inflow_outflow_timeline.png')
    plt.close()

    print(f"Success! 15 charts have been generated and saved to the '{output_dir}' directory.")

if __name__ == "__main__":
    create_visualizations()