#from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, get_object_or_404
from django.views import generic
from .models import Entity, Industry, ChartColour
from common.utils import Utils
from common import common_bo
import json

from common import constanst #_bo

configuration = common_bo.get_configuration()

# Create your views here.

class EntityListView(generic.ListView):
    template_name = constanst.ENTITY_TEMPLATE_LISTVIEW
    context_object_name =  constanst.CURRENT_CONTEXT

    def get_queryset(self):
        entities =  Entity.objects.filter(is_deleted = False).order_by('-created_date')[:5]
        return {'configuration': configuration, 'list_entities': entities}
        #return { 'list_entities': entities}
    #latest_question_list = Question.objects.order_by('pub_date')[:5]
    #template = loader.get_template('Polls/index.html')
    #context = {'latest_question_list': latest_question_list,}
    ##return HttpResponse(template.render(context, request))
    #return render(request, 'Polls/index.html', context)

def all_colours():        
    colours = []
    allColours = ChartColour.objects.all()
    for colour in allColours:
        colours.append({'fill': colour.fill, 'stroke': colour.stroke})

    return colours

class EntityDetailView(generic.DetailView):
    model = Entity
    template_name = constanst.ENTITY_TEMPLATE_DETAILS_VIEW
    context_object_name =  constanst.CURRENT_CONTEXT
        

    def get_object(self, **kwargs):
        # Call the base implementation first to get a context
        entity = super().get_object()

        view_data = {};

        view_data["configuration"] = configuration
        view_data["colours"] =  all_colours()
        view_data["entity"] =  entity 

        #balance sheet

        year_balance_sheet = entity.year_balance_sheet()
        firstDict = next(iter(year_balance_sheet.values()))
        balance_sheet_fields = firstDict.keys()
        #assets_chart = json.dumps(entity.get_asset_structure_year())
        assets_chart = entity.get_asset_structure_year()
        assets_structure_and_growth_by_year = entity.assets_structure_and_growth_by_year()
        equity_structure_and_growth_by_year = entity.equity_structure_and_growth_by_year()

        assets_structure_and_growth_percent_by_year = entity.assets_structure_and_growth_percent_by_year()
        equity_structure_and_growth_percent_by_year = entity.equity_structure_and_growth_percent_by_year()

        liquidity_ratio_by_year = entity.liquidity_ratio_by_year()

        

        view_data["year_balance_sheet"] =  year_balance_sheet
        view_data["assets_chart"] =  assets_chart
        
        view_data["equity_structure_and_growth_by_year"] =  equity_structure_and_growth_by_year
        view_data["assets_structure_and_growth_by_year"] =  assets_structure_and_growth_by_year
        view_data["assets_structure_and_growth_percent_by_year"] =  assets_structure_and_growth_percent_by_year
        view_data["equity_structure_and_growth_percent_by_year"] =  equity_structure_and_growth_percent_by_year
        view_data["liquidity_ratio_by_year"] =  liquidity_ratio_by_year
        view_data["balance_sheet_fields"] =  balance_sheet_fields

        #income statement

        income_statement_structure_growth_by_year = entity.income_statement_structure_growth_by_year()
        view_data["income_statement_structure_growth_by_year"] =  income_statement_structure_growth_by_year

        income_statement_structure_growth_by_year_type1 = entity.income_statement_structure_growth_by_year_type1()

        view_data["income_statement_structure_growth_by_year_type1"] =  income_statement_structure_growth_by_year_type1

        profitability_ratio_by_year = entity.profitability_ratio_by_year()
        view_data["profitability_ratio_by_year"] =  profitability_ratio_by_year

        dupont_by_year = entity.dupont_by_year()
        view_data["dupont_by_year"] =  dupont_by_year

        turnover_ratio = entity.turnover_ratio()
        view_data["turnover_ratio"] =  turnover_ratio

        return view_data


    