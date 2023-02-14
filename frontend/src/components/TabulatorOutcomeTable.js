import React, { useContext, useState, useEffect } from "react";
import 'react-tabulator/lib/css/tabulator_simple.min.css'; // theme
import 'react-tabulator/lib/styles.css';
import { ReactTabulator, reactFormatter } from 'react-tabulator'
import { faHeart as farHeart } from "@fortawesome/free-regular-svg-icons";
import { faHeart as fasHeart } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import AuthContext from "../store/auth-context";
import MarketContext from "../store/market-context";
import BetslipContext from "../store/betslip-context";
import { useNavigate } from 'react-router-dom';

function TabulatorOutcomeTable(props){
    const authCtx = useContext(AuthContext);
    const marketCtx = useContext(MarketContext);
    const betslipCtx = useContext(BetslipContext);

    const [csrf, setCSRF] = useState(null);
    const [columns, setColumns] = useState([]);

    const navigate = useNavigate();
    const nav = (path) => {
        navigate(path);
    }

    useEffect(() => {
        if (authCtx.csrfToken === null) {
            authCtx.getSession();
        }
    }, [authCtx.isLoggedIn]);
    
    function columnsHandler (column_params){
        const columns = [];
        if (column_params.player===true) {
            columns.push(
                {title: "Player", field: "player", headerFilter: "select", headerFilterFunc: "in", headerFilterParams: {values: true, sortValuesList: "asc", multiselect: true, valuesLookup: true}},
                {title: "Position", field: "position", headerFilter: "select", headerFilterFunc: "in", headerFilterParams: {values: true, sortValuesList: "asc", multiselect: true, valuesLookup: true}},
            );
        }
        
        columns.push(
            {title: "Team", field: "team", headerFilter: "select", headerFilterFunc: "in", headerFilterParams: {values: true, sortValuesList: "asc", multiselect: true, valuesLookup: true}},
            {title: "Game", field: "game", formatter: "textarea", headerFilter: "select", headerFilterFunc: "in", headerFilterParams: {values: true, sortValuesList: "asc", multiselect: true, valuesLookup: true}},
            {title: "Prop", field: "prop", headerFilter: "select", headerFilterFunc: "in", headerFilterParams: {values: true, sortValuesList: "asc", multiselect: true, valuesLookup: true}},
        );
        if (column_params.single_outcome_type===true){
            columns.push(
                {title: "Side", field: "ot1_outcome_type", headerFilter: "select", headerFilterFunc: "in", headerFilterParams: {values: true, sortValuesList: "asc", multiselect: true, valuesLookup: true}},
            );
        }
        var counter = 0;
        column_params.outcome_types.forEach((item) => {
            counter++;
            const ot_label = "ot" + counter;
            if (item.line===true){
                columns.push(
                    {
                        title: "Best " + item.title + " @ my books",
                        columns: [
                            {title: "Best line", field: ot_label+"_best_line", cellClick: function(e, cell){betClick(e, cell, ot_label)}},
                            {title: "Odds", field: ot_label+"_best_odds", cellClick: function(e, cell){betClick(e, cell, ot_label)}},
                            {title: "Books", field: ot_label+"_books", formatter: "textarea", cellClick: function(e, cell){betClick(e, cell, ot_label)}},
                            {title: "Watchlist", formatter:reactFormatter(<HeartIcon outcome={ot_label}/>), hozAlign: "center", vertAlign: "middle"},
                        ],
                    },
                );
            }
            else {
                columns.push(
                    {
                        title: "Best " + item.title + " @ my books",
                        columns: [
                            {title: "Best odds", field: ot_label+"_best_odds", cellClick: function(e, cell){betClick(e, cell, ot_label)}},
                            {title: "Books", field: ot_label+"_books", formatter: "textarea", cellClick: function(e, cell){betClick(e, cell, ot_label)}},
                            {title: "Watchlist", formatter:reactFormatter(<HeartIcon outcome={ot_label}/>), hozAlign: "center", vertAlign: "middle"},
                        ],
                    },
                );
            }
        });
        return columns;
    }
    
    // Helper function to get info about market that is common to all books (i.e., excludes pricing)
    function parseMarket(market){
        if (market.betting_market_type==2 && market.player != null) {
            return {
                player_name: market.player.full_name,
                player_team: market.player.current_team,
                player_position: market.player.position,
                team: market.team,
                betting_event_name: market.betting_event.betting_event_name,
                betting_event_datetime: market.betting_event.start_datetime,
                betting_period_type: market.betting_period_type,
                bet_type: market.bet_type,
                market_id: market.id,
            };
        }
        else if (market.betting_market_type===3 && market.team != null){
            return {
                team: market.team,
                betting_event_name: market.betting_event.betting_event_name,
                betting_event_datetime: market.betting_event.start_datetime,
                betting_period_type: market.betting_period_type,
                bet_type: market.bet_type,
                market_id: market.id,
            };
        }
        else {
            return {
                betting_event_name: market.betting_event.betting_event_name,
                betting_event_datetime: market.betting_event.start_datetime,
                betting_period_type: market.betting_period_type,
                bet_type: market.bet_type,
                market_id: market.id,
            }
        }
    }

    // Helper function to find best value and odds for each outcome type in market
    function sortPrices(outcome_type, sportsbooks){
        console.log(outcome_type);
        if (outcome_type.bets != null) {
            const prices = outcome_type.bets.filter(p => sportsbooks.includes(p.sportsbook));
            if (prices.length > 0){
                var best_value;
                var outcomes_best_payout_american;
                var best_payout_american;
                if (outcome_type.betting_outcome_type==='Over'){
                    best_value = Math.min(...prices.map(p => p.most_recent_value));
                }
                else if (outcome_type.betting_outcome_type==='Under'){
                    best_value = Math.max(...prices.map(p => p.most_recent_value));
                }
                if (best_value !== null && Math.abs(best_value) != Infinity){
                    const outcomes_best_value = prices.filter(p => p.most_recent_value == best_value);
                    best_payout_american = Math.max(...outcomes_best_value.map(o => o.most_recent_payout_american));
                    outcomes_best_payout_american = outcomes_best_value.filter(o => o.most_recent_payout_american == best_payout_american);
                }
                else {
                    best_payout_american = Math.max(...prices.map(o => o.most_recent_payout_american));
                    outcomes_best_payout_american = prices.filter(o => o.most_recent_payout_american == best_payout_american);
                }
                const best_sportsbooks = outcomes_best_payout_american.map(o => o.sportsbook);
                const betting_outcome_ids = outcomes_best_payout_american.map(o => o.most_recent_price_update);
                return {
                    betting_market_outcome_type_id: outcome_type.id,
                    outcome_type: outcome_type.betting_outcome_type,
                    best_value: (best_value ? best_value : 'NA'),
                    best_payout_american: best_payout_american,
                    best_sportsbooks: best_sportsbooks,
                    betting_outcome_ids: betting_outcome_ids, 
                };
            }
        }
        return priceErrorHandler();
    }

    // Helper function to return values if sortPrices experiences error
    function priceErrorHandler(){
        return {
            outcome_type: '',
            best_value: 'NA',
            best_payout_american: 'NA',
            best_sportsbooks: []
        }
    }

    // Helper function to combine names of all sportsbooks that have best price
    function joinBooks(books){
        if (books.length > 0){
            return books.join("\r\n");
        }
        else {
            return 'NA';
        }
    }

    // Helper function to parse sorted prices for a market outcome type
    function parseSortedPrices(outcome_type_prices, outcome_number){
        const ot_label = 'ot' + outcome_number;
        let price_dict = {};
        price_dict[ot_label + "_outcome_type"] = outcome_type_prices.outcome_type;
        price_dict[ot_label + "_best_line"] = outcome_type_prices.best_value;
        price_dict[ot_label + "_best_odds"] = outcome_type_prices.best_payout_american;
        price_dict[ot_label + "_outcome_ids"] = outcome_type_prices.betting_outcome_ids;
        price_dict[ot_label + "_books"] =  joinBooks(outcome_type_prices.best_sportsbooks);
        price_dict[ot_label + "_betting_market_outcome_type_id"] = outcome_type_prices.betting_market_outcome_type_id;
        return price_dict;
    }

    // Helper function to convert JSON to data for tabulator
    function parseMarketData(props){
        const tabulator_data = [];
        var row_counter = 0;
        props.data.forEach((item) => {
            let output_dict = {};
            var outcome_counter=0;
            item.betting_market_outcome_types.forEach((mot) => {
                if (((props.watchlist==='true')&&(marketCtx.watchlist.includes(mot.id)))||(mot.betting_outcome_type.toLowerCase()===props.column_params.outcome_types[0].title)){
                    let outcome_type_prices=sortPrices(mot, props.sportsbooks);
                    output_dict = {...output_dict, ...parseSortedPrices(outcome_type_prices, 1)};
                    outcome_counter++;
                }
                else if ((props.column_params.outcome_types.length>1)&&(mot.betting_outcome_type.toLowerCase()===props.column_params.outcome_types[1].title)){
                    let outcome_type_prices=sortPrices(mot, props.sportsbooks);
                    output_dict = {...output_dict, ...parseSortedPrices(outcome_type_prices, 2)};
                    outcome_counter++;
                }
                if (outcome_counter===props.column_params.outcome_types.length){
                    const market=parseMarket(item);
                    row_counter++;
                    const mkt_dict = {
                        id: row_counter,
                        market_type_id: item.betting_market_type,
                        market_id: market.market_id,
                        game: market.betting_event_name + '\r\n' + market.betting_event_datetime,
                        prop: market.bet_type,
                    };
                    output_dict = {...output_dict, ...mkt_dict};
                    if (item.betting_market_type===2){
                        const ot_player_dict = {
                            player: market.player_name,
                            team: market.player_team,
                            position: market.player_position,
                        };
                        output_dict = {...output_dict, ...ot_player_dict};
                    }
                    else if (item.betting_market_type===3) {
                        const ot_team_dict = {
                            player: 'NA',
                            position: 'NA',
                            team: market.team,
                        };
                        output_dict = {...output_dict, ...ot_team_dict};
                    }
                    if (Object.keys(output_dict).length > 0){
                        tabulator_data.push(output_dict);
                        outcome_counter=0;
                    }
                }
            });
        });
        return tabulator_data;
    }

    // Heart icon
    function HeartIcon(props) { //plain text value
        const cellData = props.cell._cell.row.data;
        const mot_id = props.outcome==='ot1' ? cellData.ot1_betting_market_outcome_type_id : cellData.ot2_betting_market_outcome_type_id;
        function watchlistClick() {
            if (!authCtx.isLoggedIn) {
                nav('/auth');
            }
            else {
                marketCtx.edit_watchlist(mot_id, csrf);
            }
        }
        if (marketCtx.watchlist.includes(mot_id)){
            return <FontAwesomeIcon icon={fasHeart} onClick={watchlistClick}/>;
        } else {
            return <FontAwesomeIcon icon={farHeart} onClick={watchlistClick}/>;
        }
    }


    function betClick(e, cell, ot_label) {
        if (!authCtx.isLoggedIn) {
            nav('/auth');
        }
        else {
            const cellData = cell._cell.row.data;
            console.log(ot_label);
            betslipCtx.bet(cellData, ot_label);
            betslipCtx.modalToggle();
            console.log('betbutton');
            console.log(cellData);
            console.log(betslipCtx.showModal);
        }
    }


    // Return component JSX
    return (
        <ReactTabulator
            data={parseMarketData(props)}
            columns={columnsHandler(props.column_params)}
            layout={"fitData"}
            columnHeaderVertAlign={"bottom"}
        />
    );
}

export default TabulatorOutcomeTable;