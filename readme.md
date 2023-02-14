# Project Bink

## Overview
Project Bink is a play-money sports betting app - it allows users to bet fake money on real sports bets offered by actual sportsbetting apps in the United States. It is currently configured to offer only single-game player and team props for the NFL but is built to easily expand to other types of bets and sports (i.e., NBA, MLB, NHL).

Bets and odds are sourced from SportsData.io, which offers free versions of its sportsbetting APIs. This API access is free because SportsData.io scrambles many of the data fields. Because of this scrambling, the bets shown on Project Bink may seem incorrect (for example, it may show a rushing yards prop for a defensive player). These seeming errors would not exist if Project Bink utilized SportsData.io's paid APIs, which offer unscrambled data.

To avoid exceeding github's file size limits, this project currently contains data for only two NFL games. Available betting markets are all for the October 2nd game between the Vikings and Saints. Some user accounts also have closed bets for the 49ers game against the Cardinals.

Project Bink's backend is written in Python using Django, while the frontend is written in React. The frontend accesses the backend utilizing Django's REST API framework and Axios for requests.

## Distinctiveness and Complexity
Of all the assignments in this course, this project is probably most similar to e-commerce in that users choose an item from a 'catalog' and 'purchase' it. However, Project Bink is distinct because its users bet on sports instead of purchasing goods. More specifically, the catalog of 'goods' for Project Bink come from an external API (SportsData.io) and has much different data than an e-commerce site (i.e., the 'line' for a prop bet, odds, multiple sportsbooks).

Project Bink's architecture is also complex and distinct from other projects in this course. The backend consists of APIs I wrote myself using Django and the front end is React - no other project in this course required participants to write as much API code as I did for this project or to use React. 

I utilized several packages and tools in this project that were not touched on in this course. For example, I utilized serializers, class-based-views, and the REST framework in Django. In React, I utilized state, context, useEffect, Refs, and useNavigate. I utilized external packages such as react-router-dom (for routing to specific pages), Tabulator (for my odds tables), reactstrap (for my navbar and betslip modal), and react-select (for my sportsbook select menu).

## List of key files
Below is a list of the most important files that I created or put the most work into. I am not including every file in the project because both Django and React automatically generate many files that I either did not edit or edited only in minor ways.

project_bink > backend app > Management folder > Commands folder:
- sd_data_update.py - this file updates data from SportsData.io; it contains functions that can update all data utilized in this project but can be configured to update only specific tables; it calls the SportsData APIs, parses the responses, and adds them to or updates the relevant Django models
- result_settle.py - this file gets results from completed bets from the SportsData.io API, updates the relevant model instances with the results, and also settles relevant bets from users (adding funds to their account if their bet won)
- update_closed_markets.py - this file is only necessary because this project utilizes the free SportsData.io API and its scrambled data. SportsData includes some unscrambled data for markets that are closed. This file pulls this data and updates relevant modal instances by replacing scrambled data with this unscrambled data.

project_bink > backend app:
- models.py - contains model definitions for all data from SportsData.io used in project as well as for user-specific data such as account balances, watchlists, and bets placed
- serializers.py - contains serializers utilized by APIs in views.py that provide data to the front end; most importantly, contains serializers that provide data on available betting markets
- urls.py - contains paths for function-based view APIs
- views.py - contains both function-based and class-based views for backend APIs; most important views include 'OddsFeedBettingMarketView' (populates odds tables in front end), get_csrf (provides csrf token so front end can make POST requests to other APIs), and place_bet (places a specific bet for a user and adjusts their account balance)

project_bink > project_bink:
- urls.py - contains paths for class-based view APIs utilizing router from rest_framework, and includes paths from urls.py in backend app

project_bink:
- requirements.txt - list of dependencies for backend generated automatically with pip freeze


frontend > src > components:
- auth folder - React components for user registration and login as well as formatting currency (included in auth because user's account balance is part of auth context)
- layout folder - React components for universal layout and navbar
- Betslip.js - modal that pops up when user clicks relevant cells in odds table and allows them to place a bet
- MyBetsTable.js - React component for tables that show all bets a user has made
- SportsbookSelect.js - React component for select menu that allows user to choose which sportsbooks are included in odds table
- TabulatorOutcomeTable.js - React component for odds table; used in table that shows users all markets available in database and in table that shows all markets in user's watchlist

frontend > src > pages:
- AuthPage.js - page that allows user to either login or register; contains separate tabs for each function
- MyBetsPage.js - page that allows user to see all bets they've placed; contains separate tabs for bets that are still open and those that have closed or been canceled
- PlayerPropsOverUnder.js - page showing available markets for player props with 'over' and 'under' outcomes (i.e., # of passing yards for Patrick Mahomes)
- PlayerPropsYesNo.js - page showing available markets for player props with 'yes' outcome (i.e., Patrick Mahomes to throw more than 3 touchdowns)
- TeamPropsOverUnder.js - page showing available markets for team props with 'over' and 'under' outcomes (i.e., # of touchdowns scored by Kansas City Chiefs)
- TeamPropsYesNo.js - page showing available markets for team props with 'yes' outcome (i.e., Kansas City Chiefs to score first and lose)
- WatchlistPage.js - page that shows user all markets they've added to their watchlist

frontend > src > store:
- auth-context.js - context provider that stores user's login status, username, and account balance and contains functions that refresh the CSRF token, change user's login status, and update their account balance
- betslip-context.js - context provider that stores info about the relevant market when a user initiates a bet and manages that toggle that determines whether the betslip modal is visible to the user
- market-context.js - context provider that stores user's bet watchlist and contains function to add or remove a market from their watchlist


## Data details
Project Bink's backend includes code that updates bet data by calling SportsData.io's APIs. This code currently can only be executed via terminal but could be configured to run regularly (i.e., as a cron job) if Project Bink were deployed. 

Some of SportsData.io's data does not change frequently - for instance, it provides tables with details on NFL teams and players - while some is updated on a minute-by-minute basis (i.e., odds for specific bets). Project Bink's backend updates both types of data in the relevant Django models. 

Because SportsData.io scrambles data for its free APIs, Project Bink makes some adjustments that would not be necessary if it utilized the paid APIs. For instance, some scrambled player ID #s in the bet data do not correspond to individuals in the player dataset. When it encounters situations like these, Project Bink fills in player details with placeholders (i.e., it will set the player's name to 'x' so that the name field is not blank). 

## Key user flows

### Authentication
Users can view available bets without registering or logging in, but must authenticate to utilize Project Bink's more advanced features (e.g., placing bets, adding bets to watchlist). Users register by providing a username and password. Authentication is based on Django's contrib.auth package. On the frontend, authentication is managed by a React context provider, which allows any component to check whether the user is logged in, get their username, log out, etc. This authentication context also stores and can refresh the CSRF token required to make POST requests to the backend's APIs.

### Viewing available bets
Bets are shown to users in table format utilizing the React Tabulator package, which offers advanced features like column sorting and filtering. The table is configured to show users the best available prices for each market. For over / under bets, the optimal price is the best 'line' currently offered by a sportsbook (i.e., in a bet like 'Patrick Mahomes to throw for 300 yards', the line would be 300). For bets with only one outcome, the optimal price is the best American odds offered by a sportsbook. Users can choose which sportsbook's prices are included in this calculation in a select menu above the odds table. When a user adds or removes a sportsbook from this selection, the prices in the table are automatically updated on the client side. 

### Adding bets to watchlist
Each user can add bets to their 'watchlist' and then view all bets in their 'watchlist' on a single page linked in the main navbar at the top of the page. Users can add bets to their watchlist by clicking the heart icon in the relevant cell of the market odds table. When the user clicks the heart, the frontend makes an API call to the backend which then either adds or removes the bet from the user's watchlist. Users' watchlist is stored in a custom field added to the Django AbstractUser model. 

The heart icon for bets in the user's watchlist are a solid dark color, while the heart for all other bets is just an outline. The user's watchlist is stored client-side in a React context provider so that any page that needs to can access it.

### Placing bets
Users can place a bet using fake money. Each user is given $100 in fake money at registration and can use these funds to place bets. To place a bet, users click the 'bet' button on the far right of the odds table, which triggers a 'betslip' total where the user can then enter the amount they want to wager and submit the bet. The betslip validates the wager amount to ensure it is positive and does not exceed the user's current account balance. The betslip also shows the amount the user will win if their bet is successful - this number is updated whenever the user changes the wager amount.

When a user submits the betslip, the frontend submits a POST request to a backend API, which creates and saves an instance of the 'UserBet' model and deducts the wager amount from the user's account balance. The user's account balance displayed in the navbar is immediately updated.

Users can view all of their bets on the 'MyBets' page linked in the navbar. This page has separate tabs for 'open' bets - essentially all bets for events that have not yet taken place - and 'closed' bets.

The file 'result_settle.py' contains code that pulls results from the SportsData.io API, updates the results fields of the relevant UserBet model instances, and add funds to user's balances for any bets they won. In the current configuration, this code must be run manually via terminal but could be made into a cron job that runs on a regular basis.

## Django views
Project Bink utilizes both function-based-views and class-based-views. Most views are FBVs - for instance, views that register new users, place bets, and edit users' watchlists. The frontend accesses these views via Django's standard 'urlpatterns' and paths.

CBVs are utilized to provide data for the odds tables, watchlist page, and MyBets page. These views utilize serializers that compile selected fields from the relevant Django models. The frontend accesses these views via the REST framework and its router functionality.



