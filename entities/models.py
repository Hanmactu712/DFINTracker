from django.db import models
from common.models import BaseModel
from common.utils import Utils
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

# Create your models here.

class Period(models.TextChoices):
    Q1 = 'Q1', _('Q1')
    Q2 = 'Q2', _('Q2')
    Q3 = 'Q3', _('Q3')
    Q4 = 'Q4', _('Q4')
    FY = 'FY', _('FY')

class MasterData(BaseModel):
    type = models.CharField(max_length=200)
    key = models.CharField(max_length=200)
    value = models.TextField(max_length=2000)

    def __str__(self):
        return self.value

class ChartColour(BaseModel):
    name = models.CharField(max_length=50)
    fill = models.CharField(max_length=10)
    stroke = models.CharField(max_length=10)

    #@property
    def colour_display(self):
        return mark_safe("<div style='width: 50px; height: 10px;border: 2px solid {0};background-color: {1}'></div>".format(self.stroke, self.fill))

    def __str__(self):
        return self.name



class Industry(BaseModel):
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=1000)
       
    def __str__(self):
        return self.name

    class Meta:        
        verbose_name = "Industry"
        verbose_name_plural = "Industries"

class Entity(BaseModel):
    code = models.CharField(max_length = 10, unique=True)
    name = models.CharField(max_length=200)
    industry = models.ForeignKey(Industry, on_delete=models.DO_NOTHING)
    
    def years(self):
        minYear = self.balancesheet_set.order_by('year')[0]
        maxYear = self.balancesheet_set.order_by('-year')[0]
        return tuple(range(minyear,maxyear + 1))

    def turnover_ratio(self):
        data = dict()
        allIncomeStatements = self.incomestatement_set.filter(period = Period.FY ).order_by('year').all()
        allBalanceSheets = self.balancesheet_set.filter(period = Period.FY ).order_by('year').all()

        year = []
        receivable_turnover = []
        inventory_turnover = []
        account_payable_turnover = []
        total_assets_turnover = []
        fixed_assets_turnover = []
        owner_equity_turnover = []
        
        prev_balance = allBalanceSheets[0]
        
        for statement in allIncomeStatements: 
            curr_balance = allBalanceSheets.get(year = statement.year)
            #year
            year.append(statement.year)

            value = statement.net_revenue_from_sales / ((curr_balance.short_term_receivables + curr_balance.long_term_receivables 
                                                        + prev_balance.short_term_receivables + prev_balance.long_term_receivables) / 2)
            receivable_turnover.append(Utils.convert_to_string(round(value,2)))

            value = statement.costs_of_goods_sold / ((curr_balance.inventory + prev_balance.inventory )/2)
            inventory_turnover.append(Utils.convert_to_string(round(value,2)))

            value = ((statement.costs_of_goods_sold + curr_balance.inventory - prev_balance.inventory ) /2)  / ((curr_balance.current_advanced_payments_to_suppliers + curr_balance.long_term_advanced_payments_to_suppliers 
                                                        + prev_balance.current_advanced_payments_to_suppliers + prev_balance.long_term_advanced_payments_to_suppliers) /2)

            account_payable_turnover.append(Utils.convert_to_string(round(value,2)))

            value = statement.net_revenue_from_sales / ((curr_balance.total_assets + prev_balance.total_assets )/2)
            total_assets_turnover.append(Utils.convert_to_string(round(value,2)))

            value = statement.net_revenue_from_sales / ((curr_balance.fixed_assets + prev_balance.fixed_assets )/2)
            fixed_assets_turnover.append(Utils.convert_to_string(round(value,2)))

            value = statement.net_revenue_from_sales / ((curr_balance.owners_equity + prev_balance.owners_equity )/2)
            owner_equity_turnover.append(Utils.convert_to_string(round(value,2)))

            prev_balance = curr_balance

        data["years"] = year        
        data["receivable_turnover"] = {"label": "receivable_turnover", "data": receivable_turnover, "type": "line"}
        data["inventory_turnover"] = {"label": "inventory_turnover", "data": inventory_turnover, "type": "line"}
        data["account_payable_turnover"] = {"label": "account_payable_turnover", "data": account_payable_turnover, "type": "line"}
        data["total_assets_turnover"] = {"label": "total_assets_turnover", "data": total_assets_turnover, "type": "line"}
        data["fixed_assets_turnover"] = {"label": "fixed_assets_turnover", "data": fixed_assets_turnover, "type": "line"}
        data["owner_equity_turnover"] = {"label": "owner_equity_turnover", "data": owner_equity_turnover, "type": "line"}

        return data

    def dupont_by_year(self):
        data = dict()
        allIncomeStatements = self.incomestatement_set.filter(period = Period.FY ).order_by('year').all()
        allBalanceSheets = self.balancesheet_set.filter(period = Period.FY ).order_by('year').all()

        year = []
        net_income_net_income_before_tax = []
        net_income_before_tax_EBIT = []
        EBIT_sales = []
        sales_assets = []
        assets_owner_equity = []
        double_leverage_ratio = []


        for statement in allIncomeStatements: 
            balance = allBalanceSheets.get(year = statement.year)
            #year
            year.append(statement.year)
            net_income_net_income_before_tax.append(Utils.get_structure(statement.profit_after_corporate_income_tax, statement.total_accounting_profit_before_tax))

            ebit_value = statement.net_profit_from_operating_activity + statement.interest_expense

            net_income_before_tax_EBIT.append(Utils.get_structure(statement.total_accounting_profit_before_tax, ebit_value))            
            EBIT_sales.append(Utils.get_structure(ebit_value, statement.revenue_from_sales))
            sales_assets.append(Utils.get_structure(statement.revenue_from_sales, balance.total_assets))
            assets_owner_equity.append(Utils.get_structure(balance.total_assets, balance.owners_equity))
            double_leverage_ratio.append(Utils.get_structure(balance.total_assets * statement.total_accounting_profit_before_tax, balance.owners_equity * ebit_value))

        data["years"] = year        
        data["net_income_net_income_before_tax"] = {"label": "net income / net_income before tax", "data": net_income_net_income_before_tax, "type": "line"}
        data["net_income_before_tax_EBIT"] = {"label": "Net_income before tax / EBIT", "data": net_income_before_tax_EBIT, "type": "line"}
        data["EBIT_sales"] = {"label": "EBIT / sales", "data": EBIT_sales, "type": "line"}
        data["sales_assets"] = {"label": "sales / assets", "data": sales_assets, "type": "line"}
        data["assets_owner_equity"] = {"label": "Assets / Owner's Equity", "data": assets_owner_equity, "type": "line"}
        data["double_leverage_ratio"] = {"label": "Double leverage ratio","data": double_leverage_ratio, "type": "line"}

        return data

    def profitability_ratio_by_year(self):
        data = dict()
        allIncomeStatements = self.incomestatement_set.filter(period = Period.FY ).order_by('year').all()
        allBalanceSheets = self.balancesheet_set.filter(period = Period.FY ).order_by('year').all()

        year = []
        gross_profit_margin = []
        EBIT = []
        ROS = []
        ROA = []
        ROE = []

        for statement in allIncomeStatements: 
            #year
            balance = allBalanceSheets.get(year = statement.year)
            year.append(statement.year)
            gross_profit_margin.append(Utils.get_structure(statement.gross_profit_from_sales, statement.revenue_from_sales))
            EBIT.append(Utils.get_structure(statement.net_profit_from_operating_activity + statement.interest_expense, statement.revenue_from_sales))
            ROS.append(Utils.get_structure(statement.net_income, statement.revenue_from_sales))
            ROA.append(Utils.get_structure(statement.net_income, balance.total_assets))
            ROE.append(Utils.get_structure(statement.net_income, balance.owners_equity))

        data["years"] = year        
        data["gross_profit_margin"] = {"label": "Gross profit margin", "data": gross_profit_margin, "type": "line"}
        data["EBIT"] = {"label": "EBIT", "data": EBIT, "type": "line"}
        data["ROS"] = {"label": "ROS", "data": ROS, "type": "line"}
        data["ROA"] = {"label": "ROA", "data": ROA, "type": "line"}
        data["ROE"] = {"label": "ROE", "data": ROE, "type": "line"}
        
        return data

    def income_statement_structure_growth_by_year_type1(self):
        data = dict()
        allIncomeStatement = self.incomestatement_set.filter(period = Period.FY ).order_by('year').all()

        year = []
        revenue_from_sales = []
        net_revenue_from_sales = []
        gross_profit_from_sales = []
        EBIT = []
        total_accounting_profit_before_tax = []
        profit_after_corporate_income_tax = []
        net_income = []

        for statement in allIncomeStatement: 
            #year
            year.append(statement.year)
            revenue_from_sales.append(Utils.convert_to_string(statement.revenue_from_sales))
            net_revenue_from_sales.append(Utils.convert_to_string(statement.net_revenue_from_sales))

             
            #financial_revenue_and_expenses.append(Utils.convert_to_string(statement.financial_expenses 
            #                                                              - statement.interest_expense 
            #                                                              - statement.revenue_from_financing_activity 
            #                                                              + statement.selling_expenses 
            #                                                              + statement.general_administration_expenses))
            gross_profit_from_sales.append(Utils.convert_to_string(statement.gross_profit_from_sales))
            EBIT.append(Utils.convert_to_string(statement.net_profit_from_operating_activity + statement.interest_expense))
            total_accounting_profit_before_tax.append(Utils.convert_to_string(statement.total_accounting_profit_before_tax))
            profit_after_corporate_income_tax.append(Utils.convert_to_string(statement.profit_after_corporate_income_tax))            
            net_income.append(Utils.convert_to_string(statement.net_income))

        data["years"] = year        
        data["revenue_from_sales"] = {"label": "Revenue from sales", "data": revenue_from_sales, "type": "bar"}
        data["net_revenue_from_sales"] = {"label": "Net revenue from sales", "data": net_revenue_from_sales, "type": "bar"}
        data["gross_profit_from_sales"] = {"label": "Gross profit from sales", "data": gross_profit_from_sales, "type": "bar"}
        data["EBIT"] = {"label": "EBIT", "data": EBIT, "type": "bar"}
        data["total_accounting_profit_before_tax"] = {"label": "Total accounting profit before tax", "data": total_accounting_profit_before_tax, "type": "bar"}
        data["profit_after_corporate_income_tax"] = {"label": "Profit after corporate income tax", "data": profit_after_corporate_income_tax, "type": "bar"}
        data["net_income"] = {"label": "Net income", "data": net_income, "type": "bar"}
        
        return data

    def income_statement_structure_growth_by_year(self):
        data = dict()
        allIncomeStatement = self.incomestatement_set.filter(period = Period.FY ).order_by('year').all()

        year = []
        revenue_deduction = []
        costs_of_goods_sold = []
        financial_revenue_and_expenses = []
        interest_expense = []
        other_profit = []
        tax = []
        minority_interest = []
        net_income = []

        for statement in allIncomeStatement: 
            #year
            year.append(statement.year)
            revenue_deduction.append(Utils.convert_to_string(statement.revenue_deduction))
            costs_of_goods_sold.append(Utils.convert_to_string(statement.costs_of_goods_sold))

             
            #financial_revenue_and_expenses.append(Utils.convert_to_string(statement.financial_expenses 
            #                                                              - statement.interest_expense 
            #                                                              - statement.revenue_from_financing_activity 
            #                                                              + statement.selling_expenses 
            #                                                              + statement.general_administration_expenses))
            financial_revenue_and_expenses.append(Utils.convert_to_string(statement.gross_profit_from_sales - statement.net_profit_from_operating_activity + statement.interest_expense))

            interest_expense.append(Utils.convert_to_string(statement.interest_expense))
            other_profit.append(Utils.convert_to_string(statement.other_profit))
            tax.append(Utils.convert_to_string(statement.current_corporate_income_tax_expense - statement.deferred_corporate_income_tax_expense))
            minority_interest.append(Utils.convert_to_string(statement.minority_interest))
            net_income.append(Utils.convert_to_string(statement.net_income))

        data["years"] = year        
        data["net_income"] = {"label": "Net income", "data": net_income}
        data["minority_interest"] = {"label": "Minority interest", "data": minority_interest}
        data["tax"] = {"label": "Tax", "data": tax}
        data["other_profit"] = {"label": "Other profit", "data": other_profit}
        data["interest_expense"] = {"label": "Interest expense", "data": interest_expense}
        data["financial_revenue_and_expenses"] = {"label": "Financial revenue and expenses", "data": financial_revenue_and_expenses}
        data["costs_of_goods_sold"] = {"label": "Costs of goods sold", "data": costs_of_goods_sold}
        data["revenue_deduction"] = {"label": "Revenue deduction", "data": revenue_deduction}

        return data

    def liquidity_ratio_by_year(self):
        data = dict()
        allBalanceSheets = self.balancesheet_set.filter(period = Period.FY ).order_by('year').all()

        year = []
        current_ratio = []
        quick_ratio = []
        cash_ratio = []
        #net_working_capital = []

        for balance_sheet in allBalanceSheets: 
            #year
            year.append(balance_sheet.year)

            current_ratio.append(Utils.get_structure(balance_sheet.short_term_assets, balance_sheet.short_term_liabilities))
            quick_ratio.append(Utils.get_structure(balance_sheet.cash_or_equivalent + balance_sheet.short_term_financial_investment + balance_sheet.short_term_receivables , balance_sheet.short_term_liabilities))
            cash_ratio.append(Utils.get_structure(balance_sheet.cash_or_equivalent + balance_sheet.short_term_financial_investment, balance_sheet.total_equity))
            #net_working_capital.append(Utils.get_structure(balance_sheet.long_term_loan_depts, balance_sheet.total_equity))

        data["years"] = year        
        data["current_ratio"] = {"label": "Current ratio", "data": current_ratio}
        data["quick_ratio"] = {"label": "Quick ratio", "data": quick_ratio}
        data["cash_ratio"] = {"label": "Cash ratio", "data": cash_ratio}
        #data["net_working_capital"] = {"label": "Net working capital", "data": net_working_capital}

        return data

    def equity_structure_and_growth_percent_by_year(self):
        data = dict()
        allBalanceSheets = self.balancesheet_set.filter(period = Period.FY ).order_by('year').all()

        year = []
        long_term_loans_depts = []
        other_long_term_liabilities = []
        short_term_loans_depts = []
        other_short_term_liabilities = []

        paid_in_capital = []
        undistributed_earnings = []
        other_owner_equity = []

        for balance_sheet in allBalanceSheets: 
            #year
            year.append(balance_sheet.year)

            long_term_loans_depts.append(Utils.get_structure(balance_sheet.long_term_loan_depts, balance_sheet.total_equity))
            other_long_term_liabilities.append(Utils.get_structure(balance_sheet.long_term_liabilities - balance_sheet.long_term_loan_depts, balance_sheet.total_equity))
            short_term_loans_depts.append(Utils.get_structure(balance_sheet.short_term_loan_depts, balance_sheet.total_equity))    
            other_short_term_liabilities.append(Utils.get_structure(balance_sheet.short_term_liabilities - balance_sheet.short_term_loan_depts, balance_sheet.total_equity))      

            paid_in_capital.append(Utils.get_structure(balance_sheet.paid_in_capital, balance_sheet.total_equity))
            undistributed_earnings.append(Utils.get_structure(balance_sheet.undistributed_earnings, balance_sheet.total_equity))
            other_owner_equity.append(Utils.get_structure(balance_sheet.owners_equity - balance_sheet.paid_in_capital - balance_sheet.undistributed_earnings, balance_sheet.total_equity))
        
        data["years"] = year
        
        data["short_term_loans_depts"] = {"label": "Short-term loan and depts", "data": short_term_loans_depts}
        data["other_short_term_liabilities"] = {"label": "Other short-term liabilities", "data": other_short_term_liabilities}
        data["long_term_loans_depts"] = {"label": "Long-term loan and depts", "data": long_term_loans_depts}
        data["other_long_term_liabilities"] = {"label": "Other long-term liabilities", "data": other_long_term_liabilities}
        
        data["paid_in_capital"] = {"label": "Paid in capital", "data": paid_in_capital}
        data["undistributed_earnings"] = {"label": "Undistributed earnings", "data": undistributed_earnings}
        data["other_owner_equity"] = {"label": "other_owner_equity", "data": other_owner_equity}

        return data

    def assets_structure_and_growth_percent_by_year(self):
        data = dict()
        allBalanceSheets = self.balancesheet_set.filter(period = Period.FY ).order_by('year').all()

        year = []
        cash = []
        short_term_receivable = []
        short_term_financial_investment = []
        inventory = []
        other_short_term_assets = []

        fixed_assets = []
        long_term_receivable = []
        long_term_financial_investment = []
        long_term_investment_property = []
        other_long_term_assets = []

        for balance_sheet in allBalanceSheets: 
            #year
            year.append(balance_sheet.year)

            #short term assets
            cash.append(Utils.get_structure(balance_sheet.cash_or_equivalent, balance_sheet.total_assets))
            short_term_receivable.append(Utils.get_structure(balance_sheet.short_term_receivables, balance_sheet.total_assets))
            short_term_financial_investment.append(Utils.get_structure(balance_sheet.short_term_financial_investment, balance_sheet.total_assets))
            inventory.append(Utils.get_structure(balance_sheet.inventory, balance_sheet.total_assets))
            other_short_term_assets.append(Utils.get_structure(balance_sheet.short_term_assets - balance_sheet.cash_or_equivalent - balance_sheet.short_term_receivables - balance_sheet.short_term_financial_investment - balance_sheet.inventory, balance_sheet.total_assets))

            #long term assets
            fixed_assets.append(Utils.get_structure(balance_sheet.fixed_assets, balance_sheet.total_assets))
            long_term_receivable.append(Utils.get_structure(balance_sheet.long_term_receivables, balance_sheet.total_assets))
            long_term_financial_investment.append(Utils.get_structure(balance_sheet.long_term_financial_investment, balance_sheet.total_assets))
            long_term_investment_property.append(Utils.get_structure(balance_sheet.long_term_investment_property, balance_sheet.total_assets))
            other_long_term_assets.append(Utils.get_structure(balance_sheet.long_term_assests - balance_sheet.fixed_assets - balance_sheet.long_term_receivables - balance_sheet.long_term_financial_investment - balance_sheet.long_term_investment_property, balance_sheet.total_assets))


        data["years"] = year
        data["cash"] = {"label": "Cash", "data": cash}
        data["short_term_receivable"] = {"label": "Short term receivable", "data": short_term_receivable}
        data["short_term_financial_investment"] = {"label": "Short term financial investment", "data": short_term_financial_investment}
        data["inventory"] = {"label": "Inventory", "data": inventory}
        data["other_short_term_assets"] = {"label": "Other short term assets", "data": other_short_term_assets}
        data["fixed_assets"] = {"label": "Fixed assets", "data": fixed_assets}
        data["long_term_receivable"] = {"label": "Long term receivable", "data": long_term_receivable}
        data["long_term_financial_investment"] = {"label": "Long term financial investment", "data": long_term_financial_investment}
        data["long_term_investment_property"] = {"label": "Long term investment property", "data": long_term_investment_property}
        data["other_long_term_assets"] = {"label": "Other long term assets", "data": other_long_term_assets}

        return data

    def equity_structure_and_growth_by_year(self):
        data = dict()
        allBalanceSheets = self.balancesheet_set.filter(period = Period.FY ).order_by('year').all()

        year = []
        long_term_loans_depts = []
        other_long_term_liabilities = []
        short_term_loans_depts = []
        other_short_term_liabilities = []

        paid_in_capital = []
        undistributed_earnings = []
        other_owner_equity = []

        for balance_sheet in allBalanceSheets: 
            #year
            year.append(balance_sheet.year)

            #long_term_liabilities.append(Utils.convert_to_string(balance_sheet.long_term_liabilities))
            #short_term_liabilities.append(Utils.convert_to_string(balance_sheet.short_term_liabilities))      
            long_term_loans_depts.append(Utils.convert_to_string(balance_sheet.long_term_loan_depts))
            other_long_term_liabilities.append(Utils.convert_to_string(balance_sheet.long_term_liabilities - balance_sheet.long_term_loan_depts))
            short_term_loans_depts.append(Utils.convert_to_string(balance_sheet.short_term_loan_depts))    
            other_short_term_liabilities.append(Utils.convert_to_string(balance_sheet.short_term_liabilities - balance_sheet.short_term_loan_depts)) 

            paid_in_capital.append(Utils.convert_to_string(balance_sheet.paid_in_capital))
            undistributed_earnings.append(Utils.convert_to_string(balance_sheet.undistributed_earnings))
            other_owner_equity.append(Utils.convert_to_string(balance_sheet.owners_equity - balance_sheet.paid_in_capital - balance_sheet.undistributed_earnings))
        
        data["years"] = year
        
        data["short_term_loans_depts"] = {"label": "Short-term loan and depts", "data": short_term_loans_depts}
        data["other_short_term_liabilities"] = {"label": "Other short-term liabilities", "data": other_short_term_liabilities}
        data["long_term_loans_depts"] = {"label": "Long-term loan and depts", "data": long_term_loans_depts}
        data["other_long_term_liabilities"] = {"label": "Other long-term liabilities", "data": other_long_term_liabilities}
        
        data["paid_in_capital"] = {"label": "Paid in capital", "data": paid_in_capital}
        data["undistributed_earnings"] = {"label": "Undistributed earnings", "data": undistributed_earnings}
        data["other_owner_equity"] = {"label": "other_owner_equity", "data": other_owner_equity}

        return data

    def assets_structure_and_growth_by_year(self):
        data = dict()
        allBalanceSheets = self.balancesheet_set.filter(period = Period.FY ).order_by('year').all()

        year = []
        cash = []
        short_term_receivable = []
        short_term_financial_investment = []
        inventory = []
        other_short_term_assets = []

        fixed_assets = []
        long_term_receivable = []
        long_term_financial_investment = []
        long_term_investment_property = []
        other_long_term_assets = []

        for balance_sheet in allBalanceSheets: 
            #year
            year.append(balance_sheet.year)

            #short term assets
            cash.append(Utils.convert_to_string(balance_sheet.cash_or_equivalent))
            short_term_receivable.append(Utils.convert_to_string(balance_sheet.short_term_receivables))
            short_term_financial_investment.append(Utils.convert_to_string(balance_sheet.short_term_financial_investment))
            inventory.append(Utils.convert_to_string(balance_sheet.inventory))
            other_short_term_assets.append(Utils.convert_to_string(balance_sheet.short_term_assets - balance_sheet.cash_or_equivalent - balance_sheet.short_term_receivables - balance_sheet.short_term_financial_investment - balance_sheet.inventory))

            #long term assets
            fixed_assets.append(Utils.convert_to_string(balance_sheet.fixed_assets))
            long_term_receivable.append(Utils.convert_to_string(balance_sheet.long_term_receivables))
            long_term_financial_investment.append(Utils.convert_to_string(balance_sheet.long_term_financial_investment))
            long_term_investment_property.append(Utils.convert_to_string(balance_sheet.long_term_investment_property))
            other_long_term_assets.append(Utils.convert_to_string(balance_sheet.long_term_assests - balance_sheet.fixed_assets - balance_sheet.long_term_receivables - balance_sheet.long_term_financial_investment - balance_sheet.long_term_investment_property))


        data["years"] = year
        data["cash"] = {"label": "Cash", "data": cash}
        data["short_term_receivable"] = {"label": "Short term receivable", "data": short_term_receivable}
        data["short_term_financial_investment"] = {"label": "Short term financial investment", "data": short_term_financial_investment}
        data["inventory"] = {"label": "Inventory", "data": inventory}
        data["other_short_term_assets"] = {"label": "Other short term assets", "data": other_short_term_assets}
        data["fixed_assets"] = {"label": "Fixed assets", "data": fixed_assets}
        data["long_term_receivable"] = {"label": "Long term receivable", "data": long_term_receivable}
        data["long_term_financial_investment"] = {"label": "Long term financial investment", "data": long_term_financial_investment}
        data["long_term_investment_property"] = {"label": "Long term investment property", "data": long_term_investment_property}
        data["other_long_term_assets"] = {"label": "Other long term assets", "data": other_long_term_assets}

        return data

    def get_asset_structure_year(self):
        assest_structure = dict()
        allBalanceSheets = self.balancesheet_set.filter(period = Period.FY ).order_by('year').all()

        for balance_sheet in allBalanceSheets:           
            short_term_assets_ratio = Utils.get_structure(balance_sheet.short_term_assets, balance_sheet.total_assets)
            long_term_assets_ratio = Utils.get_structure(balance_sheet.long_term_assests, balance_sheet.total_assets)

            structure = {'Assets_structure' : { 'labels' : ['short_term','long_term'], 'data': [short_term_assets_ratio, long_term_assets_ratio]}}

            liabilities_ratio = Utils.get_structure(balance_sheet.liabilities, balance_sheet.total_equity)
            owners_equity_ratio = Utils.get_structure(balance_sheet.owners_equity, balance_sheet.total_equity)

            structure["Equity_structure"] = {'labels' : ['liabilities','owners_equity'], 'data': [liabilities_ratio, owners_equity_ratio]}

            assest_structure[balance_sheet.year] = structure

        return assest_structure

    def get_increment_chart(self):
        chart_data = dict()
        allBalanceSheets = self.balancesheet_set.filter(period = Period.FY ).order_by('year').all()

        for balance_sheet in allBalanceSheets:           
            short_term_assets_ratio = Utils.get_structure(balance_sheet.short_term_assets, balance_sheet.total_assets)
            long_term_assets_ratio = Utils.get_structure(balance_sheet.long_term_assests, balance_sheet.total_assets)

            structure = {'Assets_structure' : { 'labels' : ['short_term','long_term'], 'data': [short_term_assets_ratio, long_term_assets_ratio]}}

            liabilities_ratio = Utils.get_structure(balance_sheet.liabilities, balance_sheet.total_equity)
            owners_equity_ratio = Utils.get_structure(balance_sheet.owners_equity, balance_sheet.total_equity)

            structure["Equity_structure"] = {'labels' : ['liabilities','owners_equity'], 'data': [liabilities_ratio, owners_equity_ratio]}

            chart_data[balance_sheet.year] = structure

        return chart_data

    def year_balance_sheet(self):
        blanceSheetResult = dict()
        allBalanceSheets = self.balancesheet_set.filter(period = Period.FY ).order_by('year').all()

        prev = allBalanceSheets[0]
        for i in range(0, allBalanceSheets.count()):            
            curr = allBalanceSheets[i]
            year = curr.year
            #currBalanceValue = {}
            real = curr.total_assets 
            change = Utils.get_change(prev.total_assets, curr.total_assets)
            currBalanceValue = {'total_assets': {'real': real, 'change': change}}
            
            real = curr.short_term_assets 
            change = Utils.get_change(prev.short_term_assets, curr.short_term_assets)
            currBalanceValue['short_term_assets'] = {'real': real, 'change': change}
            
            
            real = curr.short_term_financial_investment 
            change = Utils.get_change(prev.short_term_financial_investment, curr.short_term_financial_investment)
            currBalanceValue['short_term_financial_investment'] = {'real': real, 'change': change}

            real = curr.short_term_receivables 
            change = Utils.get_change(prev.short_term_receivables, curr.short_term_receivables)
            currBalanceValue['short_term_receivables'] = {'real': real, 'change': change}

            real = curr.current_trade_receivables 
            change = Utils.get_change(prev.current_trade_receivables, curr.current_trade_receivables)
            currBalanceValue['current_trade_receivables'] = {'real': real, 'change': change}

            real = curr.current_advanced_payments_to_suppliers 
            change = Utils.get_change(prev.current_advanced_payments_to_suppliers, curr.current_advanced_payments_to_suppliers)
            currBalanceValue['current_advanced_payments_to_suppliers'] = {'real': real, 'change': change}
            
            real = curr.intra_company_current_receivables 
            change = Utils.get_change(prev.intra_company_current_receivables, curr.intra_company_current_receivables)
            currBalanceValue['intra_company_current_receivables'] = {'real': real, 'change': change}

            real = curr.receivables_based_on_stages_of_construction_contract_schedule 
            change = Utils.get_change(prev.receivables_based_on_stages_of_construction_contract_schedule, curr.receivables_based_on_stages_of_construction_contract_schedule)
            currBalanceValue['receivables_based_on_stages_of_construction_contract_schedule'] = {'real': real, 'change': change}
            
            real = curr.current_loans_receivable 
            change = Utils.get_change(prev.current_loans_receivable, curr.current_loans_receivable)
            currBalanceValue['current_loans_receivable'] = {'real': real, 'change': change}
            
            real = curr.provision_for_current_doubt_debts 
            change = Utils.get_change(prev.provision_for_current_doubt_debts, curr.provision_for_current_doubt_debts)
            currBalanceValue['provision_for_current_doubt_debts'] = {'real': real, 'change': change}
            
            real = curr.other_current_receivables 
            change = Utils.get_change(prev.other_current_receivables, curr.other_current_receivables)
            currBalanceValue['other_current_receivables'] = {'real': real, 'change': change}
            
            real = curr.inventory 
            change = Utils.get_change(prev.inventory, curr.inventory)
            currBalanceValue['inventory'] = {'real': real, 'change': change}
            
            real = curr.other_short_term_assets 
            change = Utils.get_change(prev.other_short_term_assets, curr.other_short_term_assets)
            currBalanceValue['other_short_term_assets'] = {'real': real, 'change': change}
            

            real = curr.long_term_assests 
            change = Utils.get_change(prev.long_term_assests, curr.long_term_assests)
            currBalanceValue['long_term_assests'] = {'real': real, 'change': change}
            
            real = curr.fixed_assets 
            change = Utils.get_change(prev.fixed_assets, curr.fixed_assets)
            currBalanceValue['fixed_assets'] = {'real': real, 'change': change}
             
            real = curr.tangible_fixed_assets 
            change = Utils.get_change(prev.tangible_fixed_assets, curr.tangible_fixed_assets)
            currBalanceValue['tangible_fixed_assets'] = {'real': real, 'change': change}
            
            real = curr.finance_lease_fixed_assets 
            change = Utils.get_change(prev.finance_lease_fixed_assets, curr.finance_lease_fixed_assets)
            currBalanceValue['finance_lease_fixed_assets'] = {'real': real, 'change': change}
            
            real = curr.intangible_fixed_asset 
            change = Utils.get_change(prev.intangible_fixed_asset, curr.intangible_fixed_asset)
            currBalanceValue['intangible_fixed_asset'] = {'real': real, 'change': change}
            
            real = curr.long_term_receivables 
            change = Utils.get_change(prev.long_term_receivables, curr.long_term_receivables)
            currBalanceValue['long_term_receivables'] = {'real': real, 'change': change}
            
            real = curr.long_term_trade_receivables 
            change = Utils.get_change(prev.long_term_trade_receivables, curr.long_term_trade_receivables)
            currBalanceValue['long_term_trade_receivables'] = {'real': real, 'change': change}
            
            real = curr.long_term_advanced_payments_to_suppliers 
            change = Utils.get_change(prev.long_term_advanced_payments_to_suppliers, curr.long_term_advanced_payments_to_suppliers)
            currBalanceValue['long_term_advanced_payments_to_suppliers'] = {'real': real, 'change': change}
            
            real = curr.working_capital_provided_to_sub_units 
            change = Utils.get_change(prev.working_capital_provided_to_sub_units, curr.working_capital_provided_to_sub_units)
            currBalanceValue['working_capital_provided_to_sub_units'] = {'real': real, 'change': change}
            
            real = curr.long_term_Intra_company_receivables 
            change = Utils.get_change(prev.long_term_Intra_company_receivables, curr.long_term_Intra_company_receivables)
            currBalanceValue['long_term_Intra_company_receivables'] = {'real': real, 'change': change}
            
            real = curr.long_term_loan_receivables 
            change = Utils.get_change(prev.long_term_loan_receivables, curr.long_term_loan_receivables)
            currBalanceValue['long_term_loan_receivables'] = {'real': real, 'change': change}
            
            real = curr.long_term_provision_for_doubt_debts 
            change = Utils.get_change(prev.long_term_provision_for_doubt_debts, curr.long_term_provision_for_doubt_debts)
            currBalanceValue['long_term_provision_for_doubt_debts'] = {'real': real, 'change': change}
            
            real = curr.other_long_term_receivables 
            change = Utils.get_change(prev.other_long_term_receivables, curr.other_long_term_receivables)
            currBalanceValue['other_long_term_receivables'] = {'real': real, 'change': change}
            
            real = curr.long_term_property_in_progress 
            change = Utils.get_change(prev.long_term_property_in_progress, curr.long_term_property_in_progress)
            currBalanceValue['long_term_property_in_progress'] = {'real': real, 'change': change}
            
            real = curr.long_term_investment_property 
            change = Utils.get_change(prev.long_term_investment_property, curr.long_term_investment_property)
            currBalanceValue['long_term_investment_property'] = {'real': real, 'change': change}
            
            real = curr.long_term_financial_investment 
            change = Utils.get_change(prev.long_term_financial_investment, curr.long_term_financial_investment)
            currBalanceValue['long_term_financial_investment'] = {'real': real, 'change': change}
            
            real = curr.other_long_term_assets 
            change = Utils.get_change(prev.other_long_term_assets, curr.other_long_term_assets)
            currBalanceValue['other_long_term_assets'] = {'real': real, 'change': change}
            
            real = curr.total_equity 
            change = Utils.get_change(prev.total_equity, curr.total_equity)
            currBalanceValue['total_equity'] = {'real': real, 'change': change}
            
            real = curr.liabilities 
            change = Utils.get_change(prev.liabilities, curr.liabilities)
            currBalanceValue['liabilities'] = {'real': real, 'change': change}
            
            real = curr.short_term_liabilities 
            change = Utils.get_change(prev.short_term_liabilities, curr.short_term_liabilities)
            currBalanceValue['short_term_liabilities'] = {'real': real, 'change': change}
            
            real = curr.short_term_liabilities_for_supliers 
            change = Utils.get_change(prev.short_term_liabilities_for_supliers, curr.short_term_liabilities_for_supliers)
            currBalanceValue['short_term_liabilities_for_supliers'] = {'real': real, 'change': change}
            
            real = curr.long_term_liabilities 
            change = Utils.get_change(prev.long_term_liabilities, curr.long_term_liabilities)
            currBalanceValue['long_term_liabilities'] = {'real': real, 'change': change}
            
            real = curr.owners_equity 
            change = Utils.get_change(prev.owners_equity, curr.owners_equity)
            currBalanceValue['owners_equity'] = {'real': real, 'change': change}
            
            real = curr.paid_in_capital 
            change = Utils.get_change(prev.paid_in_capital, curr.paid_in_capital)
            currBalanceValue['paid_in_capital'] = {'real': real, 'change': change}
            
            real = curr.share_premium 
            change = Utils.get_change(prev.share_premium, curr.share_premium)
            currBalanceValue['share_premium'] = {'real': real, 'change': change}
            
            real = curr.undistributed_earnings 
            change = Utils.get_change(prev.undistributed_earnings, curr.undistributed_earnings)
            currBalanceValue['undistributed_earnings'] = {'real': real, 'change': change}
            

            prev = curr

            blanceSheetResult[year] = currBalanceValue

        return blanceSheetResult

    def __str__(self):
        return self.code + '(' + self.name + ')'


    class Meta:        
        verbose_name = "Entity"
        verbose_name_plural = "Entities"

class BalanceSheet(BaseModel):
    entity = models.ForeignKey(Entity, on_delete=models.DO_NOTHING)
    year = models.IntegerField()
    period = models.CharField(max_length=2, choices=Period.choices, default=Period.Q1)
    
    #Assests
    total_assets = models.DecimalField('Total assests', default = 0, decimal_places = 2, max_digits = 18)

    #Shortterm assets
    short_term_assets = models.DecimalField('Short-term assests', default = 0, decimal_places = 2, max_digits = 18)

    cash_or_equivalent = models.DecimalField('Cash or equivalents', default = 0, decimal_places = 2, max_digits = 18)
    short_term_financial_investment = models.DecimalField('Short-term financial investment', default = 0, decimal_places = 2, max_digits = 18)

    short_term_receivables = models.DecimalField('Short-term receivables', default = 0, decimal_places = 2, max_digits = 18)
    current_trade_receivables = models.DecimalField('Current trade receivables', default = 0, decimal_places = 2, max_digits = 18)
    current_advanced_payments_to_suppliers = models.DecimalField('Current advanced payments to suppliers', default = 0, decimal_places = 2, max_digits = 18)
    intra_company_current_receivables = models.DecimalField('Intra-company current receivables', default = 0, decimal_places = 2, max_digits = 18)
    receivables_based_on_stages_of_construction_contract_schedule = models.DecimalField('Receivables based on stages of construction contract schedule', default = 0, decimal_places = 2, max_digits = 18)
    current_loans_receivable = models.DecimalField('Current loans receivable', default = 0, decimal_places = 2, max_digits = 18)    
    provision_for_current_doubt_debts = models.DecimalField('Provision for current doubt debts', default = 0, decimal_places = 2, max_digits = 18)    
    other_current_receivables = models.DecimalField('Other current receivables', default = 0, decimal_places = 2, max_digits = 18)
    

    #inventory
    inventory = models.DecimalField('Inventory', default = 0, decimal_places = 2, max_digits = 18)
    
    other_short_term_assets = models.DecimalField('Other short-term assests', default = 0, decimal_places = 2, max_digits = 18)

    #long term assets
    long_term_assests = models.DecimalField('Long-term assests', default = 0, decimal_places = 2, max_digits = 18)

    #fixed assets
    fixed_assets = models.DecimalField('Fixed assets', default = 0, decimal_places = 2, max_digits = 18)
    tangible_fixed_assets = models.DecimalField('Tangible fixed assets', default = 0, decimal_places = 2, max_digits = 18)
    finance_lease_fixed_assets = models.DecimalField('Finance lease fixed assets', default = 0, decimal_places = 2, max_digits = 18)
    intangible_fixed_asset = models.DecimalField('Intangible fixed asset', default = 0, decimal_places = 2, max_digits = 18)

    #long_term_receivables
    long_term_receivables = models.DecimalField('Long-term receivables', default = 0, decimal_places = 2, max_digits = 18)
    long_term_trade_receivables = models.DecimalField('Long-term trade receivables', default = 0, decimal_places = 2, max_digits = 18)
    long_term_advanced_payments_to_suppliers = models.DecimalField('Long-term advanced payments to suppliers', default = 0, decimal_places = 2, max_digits = 18)
    working_capital_provided_to_sub_units = models.DecimalField('Working capital provided to sub-units', default = 0, decimal_places = 2, max_digits = 18)
    long_term_Intra_company_receivables = models.DecimalField('Long-term Intra-company receivables', default = 0, decimal_places = 2, max_digits = 18)
    long_term_loan_receivables = models.DecimalField('Long-term loan receivables', default = 0, decimal_places = 2, max_digits = 18)
    long_term_provision_for_doubt_debts = models.DecimalField('Long-term Provision for doubt debts', default = 0, decimal_places = 2, max_digits = 18)
    other_long_term_receivables = models.DecimalField('Other long-term receivables', default = 0, decimal_places = 2, max_digits = 18)

    long_term_property_in_progress = models.DecimalField('Long-term property in progress', default = 0, decimal_places = 2, max_digits = 18)
    long_term_investment_property = models.DecimalField('Long-term investment property', default = 0, decimal_places = 2, max_digits = 18)
    long_term_financial_investment = models.DecimalField('Long-term financial investment', default = 0, decimal_places = 2, max_digits = 18)
    other_long_term_assets = models.DecimalField('Other long-term assets', default = 0, decimal_places = 2, max_digits = 18)

    #Equity = liabilities + equity
    total_equity = models.DecimalField('Total equity', default = 0, decimal_places = 2, max_digits = 18)

    #liabilities
    liabilities = models.DecimalField('Liabilities', default = 0, decimal_places = 2, max_digits = 18)
    short_term_liabilities = models.DecimalField('Short-term liabilities', default = 0, decimal_places = 2, max_digits = 18)
    short_term_liabilities_for_supliers = models.DecimalField('Short-term liabilities for supliers', default = 0, decimal_places = 2, max_digits = 18)
    short_term_loan_depts = models.DecimalField('Short-term loan and depts', default = 0, decimal_places = 2, max_digits = 18)
    long_term_liabilities = models.DecimalField('Long-term liabilities', default = 0, decimal_places = 2, max_digits = 18)
    long_term_loan_depts = models.DecimalField('Long-term loan and depts', default = 0, decimal_places = 2, max_digits = 18)

    #owners’ equity
    owners_equity = models.DecimalField('Owners equity', default = 0, decimal_places = 2, max_digits = 18)
    paid_in_capital = models.DecimalField('Paid-in capital', default = 0, decimal_places = 2, max_digits = 18)
    share_premium = models.DecimalField('Share premium', default = 0, decimal_places = 2, max_digits = 18)
    undistributed_earnings = models.DecimalField('Undistributed earnings', default = 0, decimal_places = 2, max_digits = 18)

    #ratio

    def current_ratio(self):
        "Returns the person's full name."
        return self.short_term_assets/self.short_term_liabilities * 100

    def quick_ratio(self):
        "Returns the person's full name."
        return (self.cash_or_equivalent + self.short_term_financial_investment + self.short_term_receivables) / self.short_term_liabilities * 100

    def cash_ratio(self):
        "Returns the person's full name."
        return (self.cash_or_equivalent + self.short_term_financial_investment) / self.short_term_liabilities * 100

    def net_working_capital(self):
        "Returns the person's full name."
        return self.short_term_assets - self.short_term_liabilities

    #def interest_coverage_ratio(self):
    #    "Returns the person's full name."
    #    return (self.cash_or_equivalent + self.short_term_financial_investment) / self.short_term_liabilities * 100

    def __str__(self):
        return "{} - {}{}".format(self.entity.code,self.period,self.year)

class IncomeStatement(BaseModel):
    entity = models.ForeignKey(Entity, on_delete=models.DO_NOTHING)
    year = models.IntegerField()
    period = models.CharField(max_length=2, choices=Period.choices, default=Period.Q1)

    revenue_from_sales = models.DecimalField('Revenue from sales', default = 0, decimal_places = 2, max_digits = 18)
    revenue_deduction = models.DecimalField('Revenue deduction', default = 0, decimal_places = 2, max_digits = 18)
    net_revenue_from_sales = models.DecimalField('Net revenue from sales', default = 0, decimal_places = 2, max_digits = 18)
    costs_of_goods_sold = models.DecimalField('Costs of goods sold', default = 0, decimal_places = 2, max_digits = 18)
    gross_profit_from_sales = models.DecimalField('Gross profit from sales', default = 0, decimal_places = 2, max_digits = 18)
    revenue_from_financing_activity = models.DecimalField('Revenue from financing activity', default = 0, decimal_places = 2, max_digits = 18)
    financial_expenses = models.DecimalField('Financial expenses', default = 0, decimal_places = 2, max_digits = 18)
    selling_expenses = models.DecimalField('Selling expenses', default = 0, decimal_places = 2, max_digits = 18)
    general_administration_expenses = models.DecimalField('General administration expenses', default = 0, decimal_places = 2, max_digits = 18)
    net_profit_from_operating_activity = models.DecimalField('Net profit from operating activity', default = 0, decimal_places = 2, max_digits = 18)
    interest_expense = models.DecimalField('Interest expense', default = 0, decimal_places = 2, max_digits = 18)    
    other_profit = models.DecimalField('Other profit', default = 0, decimal_places = 2, max_digits = 18)
    total_accounting_profit_before_tax = models.DecimalField('Total accounting profit before tax', default = 0, decimal_places = 2, max_digits = 18)
    current_corporate_income_tax_expense = models.DecimalField('Current corporate income tax expense', default = 0, decimal_places = 2, max_digits = 18)
    deferred_corporate_income_tax_expense = models.DecimalField('Deferred corporate income tax expense', default = 0, decimal_places = 2, max_digits = 18)
    profit_after_corporate_income_tax = models.DecimalField('Profit after corporate income tax', default = 0, decimal_places = 2, max_digits = 18)
    minority_interest = models.DecimalField('Minority Interest', default = 0, decimal_places = 2, max_digits = 18)
    net_income = models.DecimalField('Net Income', default = 0, decimal_places = 2, max_digits = 18)

    #ratio

    def gross_margin_ratio(self):
        "Returns the person's full name."
        return self.gross_profit_from_sales / self.net_revenue_from_sales * 100

    def Operating_margin_ratio(self):
        "Returns the person's full name."
        return self.net_profit_from_operating_activity / self.net_revenue_from_sales * 100

    #def ROA(self):
    #    "Returns the person's full name."
    #    return self.net_profit_from_operating_activity / self.net_revenue_from_sales * 100

    #def EPS(self):
    #    "Returns the person's full name."
    #    return self.net_profit_from_operating_activity / self.net_revenue_from_sales * 100

    def __str__(self):
        return "{} - {}{}".format(self.entity.code,self.period,self.year)

class CashFlow(BaseModel):
    entity = models.ForeignKey(Entity, on_delete=models.DO_NOTHING)
    year = models.IntegerField()
    period = models.CharField(max_length=2, choices=Period.choices, default=Period.Q1)

    cash_flow_generated_from_operating_activity = models.DecimalField('Cash flow generated from operating activity', default = 0, decimal_places = 2, max_digits = 18)
    income_from_sales = models.DecimalField('Revenue from sales', default = 0, decimal_places = 2, max_digits = 18)
    depreciation_distribution = models.DecimalField('Depreciation & distribution', default = 0, decimal_places = 2, max_digits = 18)
    provision = models.DecimalField('Provision', default = 0, decimal_places = 2, max_digits = 18)
    exchange_rate_differences = models.DecimalField('Exchange rate differences', default = 0, decimal_places = 2, max_digits = 18)
    income_from_investment = models.DecimalField('Income from investment', default = 0, decimal_places = 2, max_digits = 18)
    liabilities_interest = models.DecimalField('Liabilities interest', default = 0, decimal_places = 2, max_digits = 18)

    operation_income_before_working_capital_change = models.DecimalField('Operation income before working capital change', default = 0, decimal_places = 2, max_digits = 18)
    receivable_change = models.DecimalField('Receivable change', default = 0, decimal_places = 2, max_digits = 18)
    inventory_change = models.DecimalField('Inventory change', default = 0, decimal_places = 2, max_digits = 18)
    accrued_expenses_change = models.DecimalField('Accrued expenses change', default = 0, decimal_places = 2, max_digits = 18)
    advanced_payments = models.DecimalField('Advanced payments', default = 0, decimal_places = 2, max_digits = 18)
    interest_payment = models.DecimalField('Interest payment', default = 0, decimal_places = 2, max_digits = 18)
    corporate_income_tax_payment = models.DecimalField('Corporate income tax payment', default = 0, decimal_places = 2, max_digits = 18)
    other_income_from_operating_activity = models.DecimalField('Other income from operating activity', default = 0, decimal_places = 2, max_digits = 18)
    other_payments_for_operating_activity = models.DecimalField('Other payments for operating activity', default = 0, decimal_places = 2, max_digits = 18)

    cash_flow_generated_from_investing_activity = models.DecimalField('Cash flow generated from investing activity', default = 0, decimal_places = 2, max_digits = 18)
    fixed_assets_expenses = models.DecimalField('Fixed assets expenses', default = 0, decimal_places = 2, max_digits = 18)
    disposal_of_fixed_assets = models.DecimalField('Disposal of fixed assets', default = 0, decimal_places = 2, max_digits = 18)
    interest_income_dividend_distributed_profit = models.DecimalField('Interest income dividend and distributed profit', default = 0, decimal_places = 2, max_digits = 18)
    other_income_from_investing = models.DecimalField('Other income_from investing', default = 0, decimal_places = 2, max_digits = 18)
    other_payment_for_investing = models.DecimalField('Other payment for investing', default = 0, decimal_places = 2, max_digits = 18)


    cash_flow_generated_from_financing_activity = models.DecimalField('Cash flow generated from financing activity', default = 0, decimal_places = 2, max_digits = 18)
    cash_received_from_owner_paid_in_capital = models.DecimalField('Cash received from owner paid in capital', default = 0, decimal_places = 2, max_digits = 18)
    cash_payment_for_owner_paid_in_capital = models.DecimalField('Cash payment for owner paid in capital', default = 0, decimal_places = 2, max_digits = 18)
    cash_from_loan = models.DecimalField('Cash from loan', default = 0, decimal_places = 2, max_digits = 18)
    loan_return = models.DecimalField('Loan return', default = 0, decimal_places = 2, max_digits = 18)
    dividend_profit_paid_to_owner = models.DecimalField('Dividend profit paid to owner', default = 0, decimal_places = 2, max_digits = 18)
    other_income_from_financing = models.DecimalField('Other income from financing', default = 0, decimal_places = 2, max_digits = 18)
    other_payment_for_financing = models.DecimalField('Other payment for financing', default = 0, decimal_places = 2, max_digits = 18)

    def __str__(self):
        return "{} - {}{}".format(self.entity.code,self.period,self.year)