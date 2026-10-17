import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from theme import apply_app_theme, apply_chart_theme

# ---- Page styling and header ----
apply_app_theme()
st.title("Payroll analysis")
st.caption("Payroll costs, workforce movement, earnings and deductions")
st.divider()

# ---- Data loading ----
df=pd.read_parquet('Cleaned data.parquet')

# ---- Filters ----
st.markdown("##### Filter the report")
filters1 , filters2 = st.columns(2, gap="medium")

with filters1:
    dep = ['All Departments']+sorted(df['Department'].unique().tolist())
    dep_selec = st.selectbox('Department', dep)
with filters2:
    year = ['All Years'] + sorted(df['Hire Date'].dt.year.unique().tolist())
    year_selec = st.selectbox('Year' , year)

#apply_filter
filterd_data = df.copy()

if year_selec != 'All Years':
    filterd_data = filterd_data[filterd_data['Hire Date'].dt.year == year_selec]
else:
    filterd_data=df.copy()

if dep_selec != 'All Departments':
    filterd_data = filterd_data[filterd_data['Department'] == dep_selec]

# ---- Tabs ----
tab1, tab2 ,tab3 , tab4 =st.tabs([
    ':material/summarize: Overall summary',
    ':material/person_add: Onboarding details',
    ':material/trending_up: Earning details',
    ':material/trending_down: Deduction details',
])

# ===========================================================================
# Overall Summary Tab
# ===========================================================================
with tab1:

    st.subheader('Summary dashboard', icon=':material/bar_chart:')

  #First Section
    with st.container():
        col1 , col2 , col3 = st.columns(3, gap= 'medium')
        
        #first chart
        
        with col1:
            dep_summary = filterd_data.groupby('Department').agg(
                Total_Employees = ('Employee ID','nunique'),
                Total_Salaries = ('Gross Salary' , 'sum')
            ).reset_index()

            st.dataframe(
                dep_summary,
                hide_index= True,
                use_container_width=True,
                height = 350
            )
        
        #second chart
        with col2:
            with st.container(height =350 , border = False):
                total_salaries = round(filterd_data['Net Salary'].sum())
                total_employess = filterd_data['Employee ID'].nunique()
                total_earning = filterd_data['Total Variable Pay'].sum()
                total_deductions = round(filterd_data['Total Penalties'].sum())

                card1 , card2 = st.columns(2)

                with card1:
                     with st.container(height=160, border = False):
   
                        st.metric('Total salaries', f'{total_salaries: ,.0f}')

                with card2:
                    with st.container(height=160, border = False):

                        st.metric('Total employees', f'{total_employess: ,}')

                card3 , card4 = st.columns(2)

                with card3:
                     with st.container(height=160, border = False):

                        st.metric('Total earnings' , f'{total_earning: ,.0f}')
                with card4:
                     with st.container(height=160, border = False):

                        st.metric('Total deductions' , f'{total_deductions: ,.0f}')
                
        #third chart
        with col3:
            reasons_of_termination = filterd_data.groupby('Termination Reason')['Employee ID'].count().reset_index()
            fig = px.pie(data_frame=reasons_of_termination,names='Termination Reason' , values='Employee ID',title='Termination reasons')
            fig.update_layout(
            height=350,
            margin=dict(l=10, r=10, t=50, b=10))
            apply_chart_theme(fig)
            st.plotly_chart(fig,use_container_width=True)

  #Second Section
    with st.container():
        char1 , char2 = st.columns(2)

        with char1:
            filterd_data['hire_Month_overall'] = filterd_data['Hire Date'].dt.month
            filterd_data['hire_month_name_overall']= filterd_data['Hire Date'].dt.month_name()

            total_hires = (
                            filterd_data[
                                filterd_data['Hire Date'].dt.year == 2026
                                ]
                            .groupby(
                                ['hire_Month_overall' , 'hire_month_name_overall']
                                )['Employee ID']
                            .nunique()
                            .reset_index().sort_values(by='hire_Month_overall')
                            )
            hire_overall_pie = px.line(data_frame=total_hires , x='hire_month_name_overall' , y='Employee ID',text='Employee ID',title ='New hires',labels ={'Employee ID': 'Total Employees' , 'hire_month_name_overall': 'Month'}).update_traces(textposition = 'top center')
        
            apply_chart_theme(hire_overall_pie)
            st.plotly_chart(hire_overall_pie, use_container_width = True , key='overall_hires')
        
        with char2:
            total_increase_per_month = (
            filterd_data.groupby(['Month_num', 'Salaries Month'])['Monthly Increase'].sum()
            .reset_index()
            .sort_values('Month_num'))

            bar_char =px.bar(data_frame=total_increase_per_month,
            x='Salaries Month',
            y='Monthly Increase',
            title = 'Raises per month',
            labels = {

                'Salaries Month' : 'Months',
                'Monthly Increase': 'Total Increasement'
        
                },
            text_auto= True)

            apply_chart_theme(bar_char)
            st.plotly_chart(bar_char, use_container_width = True)

# ===========================================================================
# Onboarding Details Tab
# ===========================================================================
with tab2:

    st.subheader("Onboarding details", icon=":material/group_add:")

    with st.container():
        left , right= st.columns([2,3] , gap = 'medium')

        #left chart
        with left:
            with st.container(border = False):
                total_leaves_per_dep = filterd_data.groupby('Department').agg(Total_Leaves= ('Termination Reason','count'),
                                                                          Total_Employess = ('Employee ID' , 'nunique')
                                                                          ).reset_index()
                fig = px.bar(
                    data_frame=total_leaves_per_dep , 
                    y='Department' , 
                    x=['Total_Employess','Total_Leaves'], 
                    text_auto= True , 
                    title='Total employees and leaves per department',
                    barmode='group')
                apply_chart_theme(fig)
                st.plotly_chart(
                    fig, 
                    use_container_width = True, 
                    )

        #right chart - top

        with right:
            top_cards = st.container(height = 110 , border = False)
            with top_cards:
                total_employees_overall = 1200
                col1 , col2 , col3 = st.columns(3)
                with col1:
                    st.metric(
                        'Total Employees',
                        f'{total_employees_overall}'
                    )
                total_leaves_overall = 254
                with col2:
                    st.metric(
                        'Total Leaves',
                        f'{total_leaves_overall}'
                    )
                all_turn_over_ratio = (total_leaves_overall / total_employees_overall )*100
                with col3:
                    st.metric(
                        'Turnover ratio' , 
                        f'{all_turn_over_ratio : .1f}%'
                    )
            middle_cards = st.container()
            with middle_cards:
                cards , charts = st.columns([1,2] , gap='medium')
                with cards:             
                    total_new_hires = filterd_data[filterd_data['Hire Date'].dt.year == 2026]['Employee ID'].nunique()
                    total_new_leaves = filterd_data[filterd_data['Hire Date'].dt.year == 2026]['Termination Reason'].count()
                    turn_over_ratio = 0
                    if total_new_hires ==0:
                        turn_over_ratio == 0
                    else:
                        turn_over_ratio= (total_new_leaves / total_new_hires) * 100
                    with st.container(height = 110, border = False):
                        st.metric('2026 hires' ,f'{total_new_hires : ,}' )

                    with st.container(height = 110, border = False):
                        st.metric('2026 leaves' ,f'{total_new_leaves : ,}' )

                    with st.container(height = 110, border = False):
                        st.metric('2026 turnover ratio' ,f'{turn_over_ratio: .1f}%' )

                with charts:
                    with st.container():
                                        total_leaves_titles = (
                                                                filterd_data.groupby('Job Title')
                                                                .agg(
                                                                        Total_Employees = ('Employee ID' , 'nunique'),
                                                                        Total_Leaves= ('Termination Reason','count')
                                                                )
                                                                .reset_index())
                                        total_leaves_titles['Turnover_Ratio'] = (
                                                                total_leaves_titles['Total_Leaves']
                                                                .div(total_leaves_titles['Total_Employees'])
                                                                .mul(100)
                                                                .fillna(0)
                                                                .round()
                                                            )
                                        total_leaves_titles['Turnover_Ratio'] = (
                                                                total_leaves_titles['Turnover_Ratio'].map('{:.1f}%'.format)
                                                            )
                                        total_leaves_titles = total_leaves_titles.rename(
                                             columns={'Job Title': 'Job Title' ,
                                                      'Total_Employees' : 'Total Employees' ,
                                                      'Total_Leaves' : 'Total Leaves' , 
                                                      'Turnover_Ratio' :  'Turnover Ratio'
                                                      })
                                        
                                        st.dataframe(total_leaves_titles,
                                                        hide_index= True)
            bottom_charts = st.container()
            with bottom_charts:
                with st.container():
                                filterd_data['hire_Month'] = filterd_data['Hire Date'].dt.month
                                filterd_data['hire_month_name']= filterd_data['Hire Date'].dt.month_name()
                                total_hires = (
                                                filterd_data[
                                                    filterd_data['Hire Date'].dt.year == 2026
                                                    ]
                                                .groupby(
                                                    ['hire_Month' , 'hire_month_name']
                                                    )['Employee ID']
                                                .nunique()
                                                .reset_index().sort_values(by='hire_Month')
                                                )
                                hire_pie = px.line(data_frame=total_hires , x='hire_month_name' , y='Employee ID',text='Employee ID',title ='New hires',labels ={'Employee ID': 'Total Employees', 'hire_month_name': 'Month'}).update_traces(textposition = 'top center')
                                apply_chart_theme(hire_pie)
                                st.plotly_chart(hire_pie,use_container_width=True)                   

# ===========================================================================
# Earning Details Tab
# ===========================================================================
with tab3:
    st.subheader('Earning details', icon=':material/account_balance_wallet:')
    with st.container():
        card1 , card2, card3, card4 , card5= st.columns(5 , border =False)
        with card1:
            total_bonus = filterd_data['Bonuses and Incentives'].sum()
            st.metric(
                'Total bonus',
                f'{total_bonus: ,.0f}'
            )
        with card2:
            total_additional_allowance = filterd_data['Additional Allowance'].sum()
            st.metric(
                'Total additional allowance',
                f'{total_additional_allowance: ,.0f}'
            )
        with card3:
            total_variable_allowance = filterd_data['Variable Allowances'].sum()
            st.metric(
                'Total variable allowance',
                f'{total_variable_allowance: ,.0f}'
            )
        with card4:
            Business_Trip_Allowance = filterd_data['Business Trip Allowance'].sum()
            st.metric(
                'Total trip allowance',
                f'{Business_Trip_Allowance: ,.0f}'
            )
        with card5:
            total_other_earnings = filterd_data['Other Earnings'].sum()
            st.metric(
                'Other earnings',
                f'{total_other_earnings: ,.0f}'
            )
    with st.container():
        chart1 , chart2 = st.columns([1,1.5] , border = False)
        with chart1:

            allowance_col=[
            'Bonuses and Incentives',
            'Additional Allowance',
            'Other Earnings',
            'Variable Allowances',
            'Business Trip Allowance'
            ]

            

            allowance_dataframe_summary = (df[allowance_col].sum().reset_index())
            allowance_dataframe_summary.columns = ['Earning type' , 'Total Amount']
            

            fig_total_earning = px.bar(
                data_frame=allowance_dataframe_summary,
                x='Earning type',
                y='Total Amount',
                text_auto=True,
                title = 'Total earning amount by type'
            )

            apply_chart_theme(fig_total_earning)
            st.plotly_chart(
                fig_total_earning,
                use_container_width = True
            )

        with chart2:
            total_bonus_emp_per_month = filterd_data.groupby(['Salaries Month','Month_num']).agg(
                TotalBonus = ('Bonuses and Incentives', 'sum'),
                TotalEmployees = ('Employee ID' , 'nunique')
                ).reset_index().sort_values(by='Month_num')

            fig = make_subplots(specs=[[{"secondary_y": True}]])

            # Total Bonus
            fig.add_trace(
                go.Bar(
                    x=total_bonus_emp_per_month['Salaries Month'],
                    y=total_bonus_emp_per_month['TotalBonus'],
                    name='Total Bonus',
                    text=total_bonus_emp_per_month['TotalBonus'],
                    textposition='auto'
                ),
                secondary_y=False
            )

            # Total Employees
            fig.add_trace(
                go.Scatter(
                    x=total_bonus_emp_per_month['Salaries Month'],
                    y=total_bonus_emp_per_month['TotalEmployees'],
                    name='Total Employees',
                    mode='lines+markers+text',
                    text=total_bonus_emp_per_month['TotalEmployees'],
                    textposition='top left'
                ),
                secondary_y=True
            )

            fig.update_layout(
                title='Monthly bonus',
                xaxis_title='Month',
                legend_title='',
                hovermode='x unified'
                
            )

            fig.update_yaxes(title_text='Total Bonus', secondary_y=False)
            fig.update_yaxes(title_text='Total Employees', secondary_y=True,dtick=5)

            apply_chart_theme(fig)
            st.plotly_chart(fig, use_container_width=True)
    with st.container():
        char1 , char2 = st.columns([2,1] , gap=5 , border = False)
        with char1:
            total_bonus_per_department = filterd_data.groupby('Department')['Total Variable Pay'].sum().reset_index()
            fig_bar_dep = px.bar(
                data_frame= total_bonus_per_department,
                x='Department',
                y='Total Variable Pay',
                text_auto = True,
                labels= {
                    'Total Variable Pay': 'Total Earnings'
                },
                title = 'Total Bonus per Departments'
            )
            apply_chart_theme(fig_bar_dep)
            st.plotly_chart(
                fig_bar_dep,
                use_container_width = True
            )
        with char2:
            total_trip_emp = filterd_data[filterd_data['Business Trip Allowance']>0].groupby('Department')['Employee ID'].nunique().reset_index()
            fig_pie =px.pie(
                        data_frame=total_trip_emp,
                        names = 'Department',
                        values= 'Employee ID',
                        title ='No. trip employees',
                        hole = 0.6
                    ).update_traces(textinfo = 'label+value+percent').update_layout(showlegend =False)
            apply_chart_theme(fig_pie)
            st.plotly_chart(
                fig_pie,
                use_container_width = True
            )

# ===========================================================================
# Deduction Details Tab
# ===========================================================================
with tab4:
        st.subheader('Deduction details', icon=':material/gavel:')
        left, right = st.columns(2, gap=5)
        #left-charts
        with left:
            #left-up-charts
            with st.container(border = True):
                st.markdown("#### Total penalties")
                filtered_ded_data = filterd_data[filterd_data['Total Penalties']>0]
                with st.container():
                        card_emp , card_val= st.columns(2)
                        with card_emp:
                            total_employess_pnlties = (
                                        filtered_ded_data[
                                            'Employee ID'].nunique()
                                    )
                            st.metric(
                                'Total employees',
                                total_employess_pnlties
                            )
                        with card_val:
                            total_val = filtered_ded_data['Total Penalties'].sum().round()
                            st.metric(
                                                        'Total value',
                                                        f'{total_val: ,.0f}'
                                                    )
                total_pen_dep = filtered_ded_data.groupby(['Salaries Month' , 'Month_num']).agg(
                        TotalEmployees = ('Employee ID','nunique'),
                        Value = ('Total Penalties' , 'sum')
                    ).reset_index().sort_values(by='Month_num').round(2)
                pnlt_fig = px.line(
                        data_frame=total_pen_dep,
                        x='Salaries Month',
                        y='Value',
                        text='Value',
                        title= 'Total penalties per month'
                    ).update_traces(textposition = 'top center')
                apply_chart_theme(pnlt_fig)
                st.plotly_chart(
                        pnlt_fig,
                        use_container_width = True
                    )  
            #left-bottom-chart
            with st.container(border = True):
                st.markdown("#### Administrative penalties details")
                emp_card , val_card = st.columns(2)
                with emp_card:
                    total_employess_admin_pnlties = (
                                                        filterd_data[
                                                            filterd_data['Administrative Penalty (Days)'] > 0
                                                        ]['Employee ID'].nunique()
                                                    )

                    st.metric(
                        label="Total employees",
                        value=total_employess_admin_pnlties
                    )
                with val_card:
                    total_pnlties = filterd_data['Total Penalties'].sum().round()
                    st.metric(
                        'Total value',
                        f'{total_pnlties:,.0f}'
                    )
                
                #left-bottom-chart
                total_employess_admin_pnlties_ch = (
                            filterd_data[filterd_data['Administrative Penalty (Days)']>0].groupby('Department')
                            .agg(
                                Total_Employees=('Employee ID','nunique'),
                                Total_Days=('Administrative Penalty (Days)','sum'))
                            .reset_index().round(2)
                            )
                admin_pnlt = px.bar(data_frame=total_employess_admin_pnlties_ch,y='Department', x=['Total_Employees','Total_Days'] , title= 'Total administrative penalty per department' , text_auto = True, barmode='group')
                apply_chart_theme(admin_pnlt)
                st.plotly_chart(admin_pnlt, use_container_width = True)

        #right-charts
        with right:
            #right-up-charts
            with st.container(border = True):
                st.markdown("#### Absence details")
                with st.container():
                    
                    totalemp , totalcal , kpi= st.columns(3)
                    with totalemp:
                    
                        total_absen_emp = (
                        filterd_data[filterd_data['Absence Days']>0]['Employee ID'].nunique()
                        )
                        st.metric(
                            'Total employees' , 
                            total_absen_emp
                        )
                    with totalcal:
                        total_val = filterd_data['Absence Deduction Amount'].sum().round()
                        st.metric(
                            'Total value',
                            f'{total_val:,.0f}'
                        )
                    with kpi:
                        absence_ratio = (filterd_data['Absence Days'].sum()// filterd_data['Employee ID'].nunique())*100
                        st.metric(
                        label = "Absence ratio",
                        value = f'{absence_ratio}%',
                        delta = "Target: 10%",
                        
                        )
                  
                filtered_absence_data = filterd_data[filterd_data['Absence Days'].notna()]
                total_employess_absence = (
                filtered_absence_data.groupby('Department')
                .agg(
                    Total_Employees=('Employee ID','nunique'),
                    Total_Absence_Days=('Absence Days','sum'),
                    Total_Absence_Penlty = ('Absence Penalty (Days)' , 'sum')
                    )
                .reset_index()
                )
                fig_absenc = px.bar(data_frame=total_employess_absence,x='Department', y=['Total_Employees','Total_Absence_Days','Total_Absence_Penlty'] , title= 'Total absence employees per department' , text_auto = True, barmode='group')
                apply_chart_theme(fig_absenc)
                st.plotly_chart(
                        fig_absenc,
                        use_container_width = True

                    )        
            #right-bottom-chart
            with st.container(border = True):
                    st.markdown("#### Statutory penalty details")
                    
                    totalemp , totalcal , pnlty_kpi = st.columns(3)
                    with totalemp:
                    
                        total_absen_emp = (
                        filterd_data[filterd_data['Statutory Penalty (Days)']>0]['Employee ID'].nunique()
                        )
                        st.metric(
                            'Total employees' , 
                            total_absen_emp
                        )
                    with totalcal:
                        total_val = filterd_data['Statutory Penalty Amount'].sum().round()
                        st.metric(
                            'Total value',
                            f'{total_val:,.0f}'
                        )
                    with pnlty_kpi:
                        pnlty_ratio = (filterd_data['Statutory Penalty (Days)'].sum()// filterd_data['Employee ID'].nunique())*100
                        st.metric(
                        label = "Absence ratio",
                        value = f'{pnlty_ratio}%',
                        delta = "Target: 4%"
                        )
                    
                    with st.container():
                        total_employess_disp_pnlties = (
                            filterd_data[filterd_data['Statutory Penalty (Days)']>0].groupby('Department')
                            .agg(
                                Total_Employees=('Employee ID','nunique'),
                                Total_Days=('Statutory Penalty (Days)','sum'))
                            .reset_index())
                    fig_discp = px.bar(data_frame=total_employess_disp_pnlties,x='Department', y=['Total_Employees','Total_Days'] , title= 'Total statutory penalty per department' , text_auto = True, barmode='group')
                    apply_chart_theme(fig_discp)
                    st.plotly_chart(
                            fig_discp,
                            use_container_width = True

                        )     