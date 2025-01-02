import pandas as pd
from typing import Dict, List
from datetime import datetime, timedelta

class VolumeAnalyzer:
    def __init__(self,target_date : str , intraday_data_path : str, day_data_path='SampleDayData.csv'):
        self.daily_data = pd.read_csv(day_data_path)
        self.daily_data['Date'] = pd.to_datetime(self.daily_data['Date'])
        self.target_date=pd.to_datetime(target_date)
        self.intraday_data=pd.read_csv(intraday_data_path)

    def calculate_30day_average(self) -> Dict[str, float]:
        prior_data = self.daily_data[self.daily_data['Date'] < self.target_date]
        #print("Hello")
        averages = {}
        for stock in prior_data['Stock Name'].unique():
            stock_data = prior_data[prior_data['Stock Name'] == stock].sort_values('Date')
            avg_volume = stock_data.tail(30)['Volume'].mean()
            averages[stock] = avg_volume
        return averages
    
    def find_volume_crossover(self, window_minutes: int = 60) -> Dict[str, List[str]]:
        daily_averages = self.calculate_30day_average()
        
        # Read and prepare intraday data
        self.intraday_data['Time'] = pd.to_datetime(self.intraday_data['Time'])
        
        # Market open time (9:15 AM)
        market_open = pd.to_datetime(self.target_date).replace(hour=9, minute=15)
        
        # Initialize results dictionary
        results = {}
        
        # Process each stock separately
        for stock in self.intraday_data['Stock Name'].unique():
            stock_data = self.intraday_data[self.intraday_data['Stock Name'] == stock].copy()
            daily_avg = daily_averages.get(stock)
            
            if daily_avg is None:
                results[stock] = None
                continue
                
            # Calculate rolling sum with 60-minute window
            window_seconds = window_minutes * 60
            stock_data = stock_data.sort_values('Time')
            stock_data['rolling_volume'] = stock_data['Last Traded Quantity'].rolling(
                window=window_seconds, min_periods=1).sum()
            # Find first crossover
            crossover = stock_data[stock_data['rolling_volume'] > daily_avg]
            
            if len(crossover) > 0:
                results[stock] = crossover.iloc[0]['Time'].strftime('%H:%M:%S')
            else:
                results[stock] = None
                
        return results

def main():
    #analyzer = VolumeAnalyzer('SampleDayData.csv')
    dates = ['2024-04-19', '2024-04-22']
    intraday_files=['19thAprilSampleData.csv','22ndAprilSampleData.csv']
    for i in range(2):
        analyzer_obj=VolumeAnalyzer(dates[i],intraday_files[i])
        results = analyzer_obj.find_volume_crossover()
        print(f"\nResults for {dates[i]}:")
        for stock, timestamps in results.items():
            print(f"{stock}: {timestamps if timestamps else None}")
    

if __name__ == "__main__":
    main()