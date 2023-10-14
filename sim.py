import random
import streamlit as st
import plotly.express as px
import pandas as pd


#Global constants
#RAINFALL_COEFFICIENT = 0.85
#CONSUMPTION_RATE_IN_LITRES = 50/1000

##Loading the data
RAIN_DATA = pd.read_csv("ClimateEngine.csv")
RAIN_DATA = RAIN_DATA[1:]
RAIN_DATA.rename(columns={'Precipitation (CHIRPS)':'Date'}, inplace=True)
RAIN_DATA.rename(columns={'Unnamed: 1':'Rain in mm3'}, inplace=True)


class roof_data:
    def __init__(self,EFFECTIVE_ROOF_AREA_M2,POPULATION_PER_HOUSEHOLD,TANK_CAPACITY_LITRES,CONSUMPTION_RATE_IN_LITRES,RAINFALL_COEFFICIENT):
        self.POPULATION_PER_HOUSEHOLD = POPULATION_PER_HOUSEHOLD
        self.RAIN_DATA = RAIN_DATA
        self.EFFECTIVE_ROOF_AREA_M2 = EFFECTIVE_ROOF_AREA_M2
        self.TANK_CAPACITY_LITRES = TANK_CAPACITY_LITRES
        self.CONSUMPTION_RATE_IN_LITRES = CONSUMPTION_RATE_IN_LITRES
        self.RAINFALL_COEFFICIENT = RAINFALL_COEFFICIENT
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
            Volume_at_the_start_m3 = self.volume_at_the_end_m3
        
        ##calculating the volume of water consumed per day(demand)

        demand_per_day = self.POPULATION_PER_HOUSEHOLD * self.CONSUMPTION_RATE_IN_LITRES/1000
        if Volume_at_the_start_m3 >= demand_per_day:
            Volume_consumed_m3 = demand_per_day
        else:
            Volume_consumed_m3 = 0
       



        ##calculating the volume in the tank at the end of the day

        volume_at_the_end_m3 = (Volume_at_the_start_m3 +Volume_Generated_m3)-Volume_consumed_m3
        if volume_at_the_end_m3>(self.TANK_CAPACITY_LITRES/1000):
            volume_at_the_end_m3=(self.TANK_CAPACITY_LITRES/1000)

        self.volume_at_the_end_m3 = volume_at_the_end_m3


        ##calculating overflow
        ##OFx= VT x-1+ RROx – MCx-TC
        overflow = max(0,Volume_at_the_start_m3 + Volume_Generated_m3 - Volume_consumed_m3 - (self.TANK_CAPACITY_LITRES/1000))
        demand_met = 1 if Volume_at_the_start_m3 >= demand_per_day else 0
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
        Daily_data=[]
        days_with_overflow = 0  # Variable to count days with overflow
        total_days = 0  # Variable to count total days
        Demand_met = 0
        Demand_not_met=0
        for _ in range(len(self.RAIN_DATA)):
            day_data = self.Generate_Daily_Volume()
            Daily_data.append(day_data)
            self.current_date += 1

            # Check for overflow and update the counts
            if day_data["Overflow (m3)"] > 0:
                days_with_overflow += 1
            total_days += 1

            if day_data["Demand Met"]>0:
                Demand_met+=1
            else:
                Demand_not_met+=1
        

        Results=[days_with_overflow,total_days,Demand_met,Demand_not_met,Daily_data]
        return Results
    def simulate_user(self):
        Daily_data=[]
        days_with_overflow = 0  # Variable to count days with overflow
        total_days = 0  # Variable to count total days
        Demand_met = 0
        Demand_not_met=0
        for _ in range(len(self.RAIN_DATA)):
            day_data = self.Generate_Daily_Volume()
            Daily_data.append(day_data)
            self.current_date += 1

            # Check for overflow and update the counts
            if day_data["Overflow (m3)"] > 0:
                days_with_overflow += 1
            total_days += 1

            if day_data["Demand Met"]>0:
                Demand_met+=1
            else:
                Demand_not_met+=1
        EFFICIENCY = (days_with_overflow/total_days*100)+1
        RELIABILITY = (Demand_met/total_days)*100
        return [EFFICIENCY,RELIABILITY]

def main():
    st.title("Rainfall Simulation Web App")
    st.sidebar.header("Input Parameters")

    # Create input widgets for Rainfall Coefficient, Consumption Rate, Effective Roof Area, and Tank Capacity
    RAINFALL_COEFFICIENT = st.sidebar.number_input("Rainfall Coefficient", min_value=0.0)
    CONSUMPTION_RATE_IN_LITRES = st.sidebar.number_input("Consumption Rate (in Litres)", min_value=0.0)
    POPULATION_PER_HOUSEHOLD = st.sidebar.number_input("Population per household",min_value=0)
    EFFECTIVE_ROOF_AREA_M2 = st.sidebar.number_input("Effective Roof Area (m2)", min_value=0.0)
    TANK_CAPACITY_LITRES = st.sidebar.number_input("Tank Capacity (Litres)", min_value=0.0)
    

    # Create a simulation button
    if st.sidebar.button("Simulate"):
        Roof = roof_data(EFFECTIVE_ROOF_AREA_M2, POPULATION_PER_HOUSEHOLD, TANK_CAPACITY_LITRES,CONSUMPTION_RATE_IN_LITRES,RAINFALL_COEFFICIENT)
        #days_with_overflow,total_days = Roof.simulate()
        simulation_results = Roof.simulate()
        #st.write(simulation_results)
        #Results=[days_with_overflow,total_days,Demand_met,Demand_not_met]
        days_with_overflow=simulation_results[0]
        total_days = simulation_results[1]
        Demand_met = simulation_results[2]
        Demand_not_met = simulation_results[3]
        # Display simulation results in a dashboard
        st.subheader("Simulation Results")
        #st.write(simulation_results)
        #((days with overflow/totaldays)*100)+1 => efficiency of the tank\
        EFFICIENCY = (days_with_overflow/total_days*100)+1
        RELIABILITY = (Demand_met/total_days)*100
        # Create charts for visualization (example: a line chart)

# Assuming you have data for the variables: days_with_overflow, total_days, Demand_met, Demand_not_met
# and simulation_results contains the data for the line chart

        pie_chart_data = {
            "Labels": ["Days with Overflow", "Days without Overflow"],
            "Values": [days_with_overflow, total_days - days_with_overflow]
            }

        pie_chart_data2 = {
            "Labels": ["Days where demand was met", "Days where demand was not met"],
            "Values": [Demand_met, Demand_not_met]
            }

        pie_chart_df2 = pd.DataFrame(pie_chart_data2)

        fig2 = px.pie(
            pie_chart_df2,
            names="Labels",
            values="Values",
            title="Reliablity"
            )

        pie_chart_df = pd.DataFrame(pie_chart_data)
        fig = px.pie(
            pie_chart_df,
            names="Labels",
            values="Values",
            title="Efficiency"
            )

# Display the pie charts in Streamlit
        st.write("Efficiency")
        st.write(EFFICIENCY)
        col1, col2 = st.columns(2)

# Display the first chart in the first column
        col1.plotly_chart(fig,use_container_width=True)

# Display the second chart in the second column
        col2.plotly_chart(fig2,use_container_width=True)

# Line chart on rainfall distribution
# Group the data into months
        Daily_data = pd.DataFrame(simulation_results[4])
        Daily_data['Date'] = pd.to_datetime(Daily_data['Date'], format="%Y-%m-%d")
        Daily_data['Month'] = Daily_data['Date'].dt.month
        Daily_data['Year'] = Daily_data['Date'].dt.year
     
        Monthly_Rain_Analysis = Daily_data.groupby('Month')['Rainfall (mm)'].sum().reset_index()
        Yearly_Rain_analysis = Daily_data.groupby('Year')['Rainfall (mm)'].sum().reset_index()
        #fig_month_rain_dist= px.bar(
        #    Monthly_Rain_Analysis,
        #    x= "Month",
        #    y= "Rainfall (mm)",
        #    orientation="v",
        #    title="<b>Rainfall distribution</b>",
        #    color_discrete_sequence=["#0083B8"]*len(Monthly_Rain_Analysis),
        #    template="plotly_white"
        #)

        
        #fig_year_rain_dist=px.bar(
        #    Yearly_Rain_analysis,
        #    x="Year",
        #    y="Rainfall (mm)",
        #    orientation="v",
        #    title="<b>Yearly Rainfall Distribution</b>",
        #    color_discrete_sequence=["#0083B8"]*len(Yearly_Rain_analysis),
        #    template="plotly_white"
        #)
        #st.plotly_chart(fig_year_rain_dist)

        #return EFFECTIVE_ROOF_AREA_M2,TANK_CAPACITY_LITRES,POPULATION_PER_HOUSEHOLD,EFFICIENCY,RELIABILITY


if __name__ == "__main__":
    main()