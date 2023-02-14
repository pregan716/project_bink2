import React from "react";
import 'react-tabulator/lib/css/tabulator_simple.min.css'; // theme
import 'react-tabulator/lib/styles.css';
import classes from './MyBets.module.css';
import { ReactTabulator } from 'react-tabulator';


function MyBetsTable (props) {
    const columns = [
        {title: "Bet", field: "bet"},
        {title: "Event", field: "event"},
        {title: "Odds", field: "odds"},
        {title: "Amount wagered", field: "wager_amount", formatter: "money", formatterParams: {symbol: "$"}},
        {title: "Date placed", field: "placed_datetime"},
        {title: "Result", field: "result"},
    ];

    function parseBetData (props) {
        const tabulator_data = [];
        props.data.forEach((item) => {
            let player = item.betting_market_outcome_type.betting_market.player !== null ? item.betting_market_outcome_type.betting_market.player.full_name : null;
            let team = item.betting_market_outcome_type.betting_market.team;
            let prop = item.betting_market_outcome_type.betting_market.bet_type;
            let outcome_type = item.betting_market_outcome_type.betting_outcome_type;
            let value = item.value;
            
            tabulator_data.push(
                {
                    bet: (player===null ? team : player) + ' ' + prop + ' ' + outcome_type + ' ' + value, // Player / Team + Prop + Outcome type + Value
                    event: item.betting_market_outcome_type.betting_market.betting_event.betting_event_name,
                    odds: item.payout_american,
                    wager_amount: item.wager_amount,
                    placed_datetime: item.placed_datetime,
                    result: item.is_win===null ? 'Open' : (item.is_win===true ? 'Win' : 'Loss')
                });
            });
        return tabulator_data;
    }

    return (
        <div className={classes.table}>
            <ReactTabulator
                data={parseBetData(props)}
                columns={columns}
                layout={"fitData"}
                columnHeaderVertAlign={"bottom"}
            />
        </div>
    );
}

export default MyBetsTable;