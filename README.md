# Taking off the Training Wheels: Re-balancing Citibike System Traffic

**Author**: Mitchell Krieger

## Overview



## Bussiness Understanding

Bike-sharing systems have a specific challenge when it comes to a user’s experience: bike stations can’t be empty because then riders will have no bike to take out. However, bike stations also shouldn’t be full because then riders will have no place to dock a bike. This dichotomy takes on additional complexity when you factor in things like the direction of rider traffic flow, time of day, weather, and hills. These elements among other user habits often will cause a Bike-share system to become “unbalanced”. The two indicators of an unbalanced system are:

- Bike Drains: Riders will take bikes out of certain areas but not return them on their commute back causing a scarcity of bikes and empty stations (Possible example causes: stations on top of hills/in a hilly area, Residential areas during the morning commute, etc)
- Bike Pools: Riders will deposit bikes but not take them out causing an abundance of bikes and no docks (Possible example causes: stations far from other modes of transit, sun setting before end of the workday)

When a system is unbalanced, the drains and pools make finding/returning a bike impossible and disrupt the user experience. Therefore the balancing of the system is a critical task for CitiBike and other bike-share systems to manage on an hourly basis. CitiBike currently uses four methods to re-balance the system:

- Bike Trains: A CitiBike employee who move bikes on specialty bike attachment, good for short distance re-balancing
- Vans: Used to collect/redistribute bikes, good for long-distance rebalancing and collecting broken bikes
- Valets: CitiBike employees who service stations where bikes are in high demand with new bikes, good for customer service
- Bike Angels: A program where riders are rewarded points for riding bikes from pools to drains, good for brand loyalty and offloading work to users

While having these methods are great, they still have to forecast where and when bikes are going to be needed and when in order to effectively deploy them. AI and Machine Learning can be used to predict where the demand for bikes will be and thus help identify where re-balancing methods need to focus their efforts. This project uses multivariate time-series anlysis to forcast bike demand and then un-supervised classification to identify bikes as pools, drains or balanced.


## Data

Live feed station data and trip history is available through [CitiBike’s open system data](https://www.citibikenyc.com/system-data). In addition, historical timestamped station data through April 2019 was collected from [The Open Bus project](https://www.theopenbus.com/methodology.html). Stations and bikes have a unique id that allows the joining of information between datasets. 

## Data Understanding:


## Methods


## Results



## Conclusions


## Next Steps



## For More Information

  
## Repository Structure

```
├──   <- 
├──   <- 
├──   <- 
├──   <- 
├──   <- 
├──   <- 
└──   <- 
