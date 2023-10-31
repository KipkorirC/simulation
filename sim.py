#importing libraries
import streamlit as st
import plotly.express as px
import pandas as pd
from dateutil import relativedelta


class roof_data:
    def __init__(self,RAIN_DATA,EFFECTIVE_ROOF_AREA_M2,POPULATION_PER_HOUSEHOLD,TANK_CAPACITY_LITRES,CONSUMPTION_RATE_IN_LITRES,RAINFALL_COEFFICIENT):
        ## variables that are used within this class
        self.POPULATION_PER_HOUSEHOLD = POPULATION_PER_HOUSEHOLD
        self.RAIN_DATA = RAIN_DATA
        self.EFFECTIVE_ROOF_AREA_M2 = EFFECTIVE_ROOF_AREA_M2
        self.TANK_CAPACITY_LITRES = TANK_CAPACITY_LITRES
        self.CONSUMPTION_RATE_IN_LITRES = CONSUMPTION_RATE_IN_LITRES
        self.RAINFALL_COEFFICIENT = RAINFALL_COEFFICIENT
        #for iteration through the data
        self.current_date= 0
    

    def Generate_Daily_Volume(self):
        RAIN_IN_MM = self.RAIN_DATA.iloc[self.current_date,:][1]
        Date=self.RAIN_DATA.iloc[self.current_date,:][0]

        ##calculating the volume of water generated from the roof
        ##RR = ERA*RAINx*RCOEFF
        Volume_Generated_m3 = self.EFFECTIVE_ROOF_AREA_M2*(RAIN_IN_MM/1000)*self.RAINFALL_COEFFICIENT

        ##calculating the volume at the start of the day
        if self.current_date==0: 
            Volume_at_the_start_m3 = 0
        else:
            Volume_at_the_start_m3 = self.volume_at_the_end_m3# previous day
        
        ##calculating the volume of water consumed per day(demand)
        demand_per_day = self.POPULATION_PER_HOUSEHOLD * self.CONSUMPTION_RATE_IN_LITRES/1000

        #logic of water is only consumed if the demand is met
        if Volume_at_the_start_m3 >= demand_per_day:
            Volume_consumed_m3 = demand_per_day
        else:
            Volume_consumed_m3 = 0
       



        ##calculating the volume in the tank at the end of the day

        volume_at_the_end_m3 = (Volume_at_the_start_m3 +Volume_Generated_m3)-Volume_consumed_m3

        ##logic to ensure that volume at the end does not exceed the tank capacity
        if volume_at_the_end_m3>(self.TANK_CAPACITY_LITRES/1000):
            volume_at_the_end_m3=(self.TANK_CAPACITY_LITRES/1000)
            

        self.volume_at_the_end_m3 = volume_at_the_end_m3



        ##calculating overflow
        ##OFx= VT x-1+ RROx – MCx-TC
        overflow = max(0,Volume_at_the_start_m3 + Volume_Generated_m3 - Volume_consumed_m3 - (self.TANK_CAPACITY_LITRES/1000))

        #calculating if demand was met(1) if it was not met(0)
        demand_met = 1 if Volume_at_the_start_m3 >= demand_per_day else 0

        #returning the data as a dictionary
        return {
            "Date":Date,
            "Rainfall (mm)": RAIN_IN_MM,
            "effective roof area":self.EFFECTIVE_ROOF_AREA_M2,
            "Tank capacity (litres)":self.TANK_CAPACITY_LITRES,
            "Volume Generated (m3)": Volume_Generated_m3,
            "Volume in Tank (Start) (m3)": Volume_at_the_start_m3,
            "Demand per Day (m3)": demand_per_day,
            "Volume Consumed (m3)": Volume_consumed_m3,
            "Volume in Tank (End) (m3)": volume_at_the_end_m3,
            "Overflow (m3)": overflow,
            "Demand Met": demand_met,
        }
    

    def simulate(self):
        Daily_data=[]#empty array
        total_days =0 # Variable to count total days
        Total_days_Demand_met = 0
        Total_volume_generated_from_roof = 0
        Total_overflow =0
        Total_rainfall = 0
        for _ in range(len(self.RAIN_DATA)):#15000
            day_data = self.Generate_Daily_Volume()
            Daily_data.append(day_data)
            self.current_date += 1
            total_days += 1
            Total_volume_generated_from_roof += day_data["Volume Generated (m3)"]
            Total_rainfall += day_data["Rainfall (mm)"]
            
            # update count of overflow
            Total_overflow +=day_data["Overflow (m3)"] 
           

            if day_data["Demand Met"]!=0:
                Total_days_Demand_met+=1
        
        Results=[total_days,Total_days_Demand_met,Daily_data,Total_overflow,Total_volume_generated_from_roof,Total_rainfall]
        return Results
def main():
    st.set_page_config(
        page_title="rainsim",
        layout="wide"
    )
    st.title("Rainfall Simulation Web App.  By Njuguna and Muthoni")
    st.markdown('##')
    st.markdown('---')


    ##sidebar
    st.sidebar.header("Input Parameters")

    # Create a file upload widget for the Excel file
    excel_file = st.sidebar.file_uploader("Upload Excel File", type=["xlsx"])
    if excel_file:
        # If a file is uploaded, read it into a DataFrame
        ## reading the data
        RAIN_DATA = pd.read_excel(excel_file,engine="openpyxl")

        RAIN_DATA = RAIN_DATA[1:]
        RAIN_DATA.rename(columns={'Precipitation (CHIRPS)':'Date'}, inplace=True)
        RAIN_DATA.rename(columns={'Unnamed: 1':'Rain in mm'}, inplace=True)
        st.sidebar.success("Excel file uploaded successfully!")

        # Create input widgets for Rainfall Coefficient, Consumption Rate, Effective Roof Area, and Tank Capacity
        RAINFALL_COEFFICIENT = st.sidebar.number_input("Rainfall Coefficient", min_value=0.0)
        CONSUMPTION_RATE_IN_LITRES = st.sidebar.number_input("Consumption Rate (in Litres)", min_value=0.0)
        POPULATION_PER_HOUSEHOLD = st.sidebar.number_input("Population",min_value=0)
        EFFECTIVE_ROOF_AREA_M2 = st.sidebar.number_input("Effective Roof Area (m2)", min_value=0.0)
        TANK_CAPACITY_LITRES = st.sidebar.number_input("Tank Capacity (Litres)", min_value=0.0)
    

    # Create a simulation button
        if st.sidebar.button("Simulate"):
            Roof = roof_data(RAIN_DATA,EFFECTIVE_ROOF_AREA_M2, POPULATION_PER_HOUSEHOLD, TANK_CAPACITY_LITRES,CONSUMPTION_RATE_IN_LITRES,RAINFALL_COEFFICIENT)
        #days_with_overflow,total_days = Roof.simulate()
            simulation_results = Roof.simulate()
        #st.write(simulation_results)
        #Results=[days_with_overflow,total_days,Demand_met,Demand_not_met]
            total_days = simulation_results[0]
            Total_days_Demand_met = simulation_results[1]
            Raw_data =pd.DataFrame(simulation_results[2])
            Total_overflow = simulation_results[3]
            Total_volume_generated_from_roof = simulation_results[4]
            Total_rainfall = simulation_results[5]

        # Display simulation results in a dashboard
           # st.subheader("Simulation Results")


        #total volume_generated_m3- total overflow/total volume generated from roof)*100
            EFFICIENCY = ((Total_volume_generated_from_roof-Total_overflow)/Total_volume_generated_from_roof)*100
            RELIABILITY = (Total_days_Demand_met/total_days)*100
        #Displaying main efficiency
            

        ##grouping the data into years and months
            Raw_data['Date'] = pd.to_datetime(Raw_data['Date'], format="%Y-%m-%d")
            Raw_data['Month'] = Raw_data['Date'].dt.strftime('%B')
            Raw_data['Year'] = Raw_data['Date'].dt.year

        ##getting the number of years of the date
            first_date = Raw_data["Date"][0]
            final_date = Raw_data["Date"][total_days-1]
            no_of_years = relativedelta.relativedelta(final_date,first_date).years
        ##calculating annual averages
            Average_annual_rainfall = Total_rainfall/no_of_years
            Average_rain_water_harvesting_potential = Total_volume_generated_from_roof/no_of_years
        ##grouping the data into years
            months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

            #Monthly_Rain_Analysis = Raw_data.groupby('Month')['Rainfall (mm)'].mean().reset_index()
            Monthly_Rain_sum = Raw_data.groupby(['Month', 'Date'])['Rainfall (mm)'].sum().reset_index()

# Group by 'Month' and calculate the sum of 'Rainfall (mm)' for each month
            Monthly_rain_mean = Monthly_Rain_sum.groupby('Month')['Rainfall (mm)'].sum().reindex(months).reset_index()
            Monthly_rain_mean['mean Rainfall(mm)'] = Monthly_rain_mean['Rainfall (mm)']/no_of_years
            Monthly_rain_mean.drop(columns='Rainfall (mm)',inplace=True)
            Yearly_Rain_analysis = Raw_data.groupby('Year')['Rainfall (mm)'].sum().reset_index()
            Yearly_Potential = Raw_data.groupby('Year')["Volume Generated (m3)"].sum().reset_index()

        
            fig_monthly_rain_dist=px.bar(
                Monthly_rain_mean,
                x='Month',
                y='mean Rainfall(mm)',
                orientation="v",
                title="<b>Monthly Rainfall Distribution</b>",
                color_discrete_sequence=["#0083B8"]*len(Monthly_rain_mean),
                template="plotly_white"
            )

                   
            fig_year_rain_dist=px.bar(
                Yearly_Rain_analysis,
                x="Year",
                y="Rainfall (mm)",
                orientation="v",
                title="<b>Yearly Rainfall Distribution</b>",
                color_discrete_sequence=["#0083B8"]*len(Yearly_Rain_analysis),
                template="plotly_white"
            )

            fig_harvesting_potential=px.bar(
                Yearly_Potential,
                x="Year",
                y="Volume Generated (m3)",
                orientation="v",
                title="<b>Yearly harvesting potential Distribution</b>",
                color_discrete_sequence=["#0083B8"]*len(Yearly_Potential),
                template="plotly_white"
            )

            

            
            left_column,middle_column, right_column = st.columns(3)
            with left_column:
                st.subheader("Total Volume Generated(m3): ")
                st.text(Total_volume_generated_from_roof)
            with middle_column:
                st.subheader("Total Rainfall(mm)")
                st.text(Total_rainfall)
            with right_column:
                st.subheader("Total Overflow(m3): ")
                st.text(Total_overflow)

            left,middle = st.columns(2)
            with left:
                st.subheader("Total days where demand was met")
                st.text(Total_days_Demand_met)
            with middle:
                st.subheader("Total days demand was not met")
                st.text(total_days-Total_days_Demand_met)

            


# Define your data for the first pie chart
            pie_chart_data = {
                "Labels": ["Efficiency", "Losses"],
                "Values": [EFFICIENCY, 100-EFFICIENCY]
            
            }

# Define your data for the second pie chart
            pie_chart_data2 = {
                "Labels": ["Days where demand was met", "Days where demand was not met"],
                "Values": [Total_days_Demand_met, total_days-Total_days_Demand_met]
            }

# Create DataFrames
            pie_chart_df = pd.DataFrame(pie_chart_data)
            pie_chart_df2 = pd.DataFrame(pie_chart_data2)

            fig2 = px.pie(
                pie_chart_df2,
                names="Labels",
                values="Values",
                title="Reliablity",
                color="Labels",
                color_discrete_map=({"Days where demand was met":"blue",
                                     "Days where demand was not met":"red"})
             )
            fig = px.pie(
                pie_chart_df,
                names="Labels",
                values="Values",
                title="Efficiency",
                color="Labels",
                color_discrete_map=({"Efficiency":"blue",
                                     "Losses":"red"})
                                       
                )

# Display the pie charts in Streamlit
            col1, col2 = st.columns(2)

# Display the first chart in the first column
            col1.plotly_chart(fig, use_container_width=True)

# Display the second chart in the second column
            col2.plotly_chart(fig2, use_container_width=True)


#displaying charts and averages between them
            st.plotly_chart(fig_year_rain_dist)
            st.subheader("Average annual Rainfall(mm)")
            st.text(Average_annual_rainfall)
            st.plotly_chart(fig_harvesting_potential)
            st.subheader("Average annual Rainwater harvesting potential (m3)")
            st.text(Average_rain_water_harvesting_potential)
            st.plotly_chart(fig_monthly_rain_dist)


            #display data
            st.write(Raw_data)


#boiler plate code....
if __name__ == "__main__":
    main()