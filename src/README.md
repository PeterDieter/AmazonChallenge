# Source Code

## MIT files
The two files on parent level (model_apply.py and model_build.py) are not to be modified as they are needed to build and apply the model. 

## dataProcess Folder
This folder includes all the code that is used to load, manipulate and plot data.

## optiCode
This folder includes all the optimization code

## ToDo's
- Implement ideas

## Ideas
For evaluating the route we can look at:

1. Objective value with data from Amazon (✓)
2. Objective value with data from OpenRoute (✓)
3. Objective value with data from OpenRoute with headings
4. Number of left curves (✓)
5. Number of traffic lights passed
6. Include number + size of packages into the data
7. Compare Solution attained by including zoneID with solution attained without zoneID. Is this deviation different for good and bad routes?
8. Check time window slack (are routes with more planned slack better?) (✓)
9. Check if next planned stop is different from nearest neighbor. E.g. for each stop, which neighbor is the next stop? Check how far it is the next planned stop would be compared to the nearest neighbor. (✓)
10. For the metaheuristic, group stops by zoneID, then do moves by swapping whole zoneIDs or stops within a zoneID