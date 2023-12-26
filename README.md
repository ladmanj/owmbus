Modbus server which is reading data from OpenWeatherMap.
The modbus part is based on pymodbus server example.
The server part maintains the configuration of the example which it's based on, the Open Weather Map server readout configuration is configured by environment variables, WEATHER_TOKEN, LAT and LON. The set of used variables is unfortunately hardcoded at the present time.

I'm a total python newbie, I just glued the code together from different examples.
There is one known problem, that if it's started when the internet connection hasn't been established yet, then it ends somewhat stuck and the periodic update isn't provided.
The workaround I use currently is to wait until ping to the openweathermap.org is successfull and then this service is run.

Respect the licenses of the original code, feel free to extend it and publish your work.
