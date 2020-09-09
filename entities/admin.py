from django.contrib import admin

# Register your models here.
from .models import Industry, Entity, BalanceSheet, IncomeStatement, CashFlow, MasterData, ChartColour

class BaseModelAdmin(admin.ModelAdmin):
    exclude = ('created_by_user_id','created_by_user_name', 'last_modified_by_user_id', 'last_modified_by_user_name','is_deleted',)
    #list_display = ('created_by_user_name',
    #'last_modified_by_user_name','is_deleted_display')
    list_max_show_all = 200
    show_full_result_count = True
    list_per_page = 3

    def save_model(self, request, obj, form, change):
        if(change == True):
            obj.last_modified_by_user_id = request.user.id
            obj.last_modified_by_user_name = request.user.username
        else:
            obj.created_by_user_id = request.user.id
            obj.created_by_user_name = request.user.username
            obj.last_modified_by_user_id = request.user.id
            obj.last_modified_by_user_name = request.user.username

        super().save_model(request, obj, form, change)
         
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for obj in formset.deleted_objects:
            obj.is_deleted = True
            obj.save()

        for instance in formset.new_objects:
            instance.created_by_user_id = request.user.id
            instance.created_by_user_name = request.user.username
            instance.last_modified_by_user_id = request.user.id
            instance.last_modified_by_user_name = request.user.username
            instance.save()

        for instance in formset.changed_objects:       
            instance[0].last_modified_by_user_id = request.user.id
            instance[0].last_modified_by_user_name = request.user.username
            instance[0].save()


class IndustryAdmin(BaseModelAdmin):
    list_display = ('name', 'created_by_user_name','created_date', 'last_modified_by_user_name','last_modified_date','is_deleted_display')
    list_display_links = ('name',)


class BalanceSheetAdmin(BaseModelAdmin):
    list_display = ('entity', 'year', 'period', 'created_by_user_name','created_date', 'last_modified_by_user_name','last_modified_date','is_deleted_display')
    list_display_links = ('period',)

class BlanceSheetInline(admin.TabularInline):
    model = BalanceSheet
    #min_num = 4
    #max_num=15
    #extra=5
    #fields = ['year','period'
    #          ,'total_assets'
    #          ,'short_term_assets', 'cash_or_equivalent', 'short_term_financial_investment' 
    #          ,'short_term_receivables', 'current_trade_receivables', 'current_advanced_payments_to_suppliers', 'intra_company_current_receivables', 'receivables_based_on_stages_of_construction_contract_schedule', 'current_loans_receivable', 'provision_for_current_doubt_debts', 'other_current_receivables'
    #          ,'inventory', 'other_short_term_assets', 'long_term_assests'
    #          , 'fixed_assets', 'tangible_fixed_assets', 'finance_lease_fixed_assets', 'intangible_fixed_asset'
    #          ,'long_term_receivables'
    #          ,'long_term_trade_receivables','long_term_advanced_payments_to_suppliers', 'working_capital_provided_to_sub_units', 'long_term_Intra_company_receivables', 'long_term_loan_receivables', 'long_term_provision_for_doubt_debts', 'other_long_term_receivables'
    #          ,'long_term_property_in_progress', 'long_term_investment_property', 'long_term_financial_investment', 'other_long_term_assets'
    #          ,'total_equity'
    #          , 'liabilities', 'short_term_liabilities', 'short_term_liabilities_for_supliers', 'long_term_liabilities'
    #          , 'owners_equity', 'paid_in_capital', 'share_premium', 'undistributed_earnings']
    exclude = ('created_by_user_id','created_by_user_name',
    'last_modified_by_user_id', 'last_modified_by_user_name','is_deleted',)
    #fieldsets = (('General', {
    #                'fields': ('year', 'period')
    #            }),
    #             ('Assets', {
    #                'fields': ('short_term_assets', 'long_term_assests')
    #            }),
    #             ('Total Equity', {
    #                'fields': ('liabilities', 'paid_in_capital',
    #                'undistributed_earnings')
    #            }),)
    #fields = ['year','period',]
    #readonly_fields = ["image_data",]
    def get_queryset(self, request):
        qs = super().get_queryset(request)        
        return qs.filter(is_deleted=False)

class IncomeStatementAdmin(BaseModelAdmin):
    list_display = ('entity', 'year', 'period', 'created_by_user_name','created_date', 'last_modified_by_user_name','last_modified_date','is_deleted_display')
    list_display_links = ('period',)

class IncomeStatementInline(admin.TabularInline):
    model = IncomeStatement
    #min_num = 4
    #max_num=15
    #extra=5
    exclude = ('created_by_user_id','created_by_user_name', 'last_modified_by_user_id', 'last_modified_by_user_name','is_deleted',)
    #fieldsets = (('General', {
    #                'fields': ('year', 'period')
    #            }),
    #             ('Assets', {
    #                'fields': ('short_term_assets', 'long_term_assests')
    #            }),
    #             ('Total Equity', {
    #                'fields': ('liabilities', 'paid_in_capital',
    #                'undistributed_earnings')
    #            }),)
    #fields = ['year','period',]
    #readonly_fields = ["image_data",]
    def get_queryset(self, request):
        qs = super().get_queryset(request)        
        return qs.filter(is_deleted=False)

class CashFlowAdmin(BaseModelAdmin):
    list_display = ('entity', 'year', 'period', 'created_by_user_name','created_date', 'last_modified_by_user_name','last_modified_date','is_deleted_display')
    list_display_links = ('period',)

class CashFlowInline(admin.TabularInline):
    model = CashFlow
    #min_num = 4
    #max_num=15
    #extra=5
    exclude = ('created_by_user_id','created_by_user_name', 'last_modified_by_user_id', 'last_modified_by_user_name','is_deleted',)
    #fieldsets = (('General', {
    #                'fields': ('year', 'period')
    #            }),
    #             ('Assets', {
    #                'fields': ('short_term_assets', 'long_term_assests')
    #            }),
    #             ('Total Equity', {
    #                'fields': ('liabilities', 'paid_in_capital',
    #                'undistributed_earnings')
    #            }),)
    #fields = ['year','period',]
    #readonly_fields = ["image_data",]
    def get_queryset(self, request):
        qs = super().get_queryset(request)        
        return qs.filter(is_deleted=False)

class EntityAdmin(BaseModelAdmin):
    list_display = ('name', 'code', 'created_by_user_name','created_date', 'last_modified_by_user_name','last_modified_date','is_deleted_display')
    list_display_links = ('code','name',)
    inlines = [BlanceSheetInline, IncomeStatementInline, CashFlowInline,]

class MasterDataAdmin(BaseModelAdmin):
    list_display = ('type','key','value', 'created_by_user_name','created_date', 'last_modified_by_user_name','last_modified_date','is_deleted_display')
    list_display_links = ('key', 'value',)

class ChartColourAdmin(BaseModelAdmin):
    list_display = ('name','colour_display', 'created_by_user_name','created_date', 'last_modified_by_user_name','last_modified_date','is_deleted_display')
    list_display_links = ('name', 'colour_display',)    

admin.site.register(Industry, IndustryAdmin)
admin.site.register(Entity, EntityAdmin)
admin.site.register(BalanceSheet, BalanceSheetAdmin)
admin.site.register(IncomeStatement, IncomeStatementAdmin)
admin.site.register(CashFlow, CashFlowAdmin)
admin.site.register(MasterData, MasterDataAdmin)
admin.site.register(ChartColour, ChartColourAdmin)