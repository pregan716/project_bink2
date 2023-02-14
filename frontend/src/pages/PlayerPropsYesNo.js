import React, { useContext, useState, useEffect } from "react";
import 'react-tabulator/lib/css/tabulator.min.css'; // theme
import 'react-tabulator/lib/styles.css';
import TabulatorOutcomeTable from "../components/TabulatorOutcomeTable";
import Select from "react-select";
import BetslipContext from "../store/betslip-context";
import Betslip from "../components/Betslip";
import MarketContext from "../store/market-context";



function PlayerPropsYesNo(){
    
    const betslipCtx = useContext(BetslipContext);
    const marketCtx = useContext(MarketContext);

    // State attributes
    const [isLoading, setLoading] = useState(true);
    const [PROPS_DATA, setData] = useState();
    const [options, setOptions] = useState([]);
    const [selectedSportsbooks, setSelectedSportsbooks] = useState([]);

    
    useEffect(() => {
        setData(marketCtx.player_props);
        console.log(marketCtx.player_props);
        setSelectedSportsbooks(getBooks(marketCtx.player_props));
    }, [marketCtx.player_props]);

    useEffect(() => {
        if (PROPS_DATA===marketCtx.player_props){
            setLoading(false);
        }
    }, [PROPS_DATA]);

    // Show temporary element until API call finishes
    if (isLoading) {
        return <div className="App">Loading...</div>;
    }

    // Helper function to get list of sportsbooks to show in select menu
    function getBooks(data) {
        const marketSportsbooks = new Set();
        var options = [];
        // Get list of sportsbooks with prices in market data
        data.map((c) =>
        c.betting_market_outcome_types.map((o) =>
            o.bets.map((p) => marketSportsbooks.add(p.sportsbook))
        )
        );

        Array.from(marketSportsbooks).map((s) =>
        options.push({"value": s, "label": s}));
        
        setOptions(options);

        return (options.map((o) => o.value));
    }

    // Handle onChange event of the sportsbook selection dropdown
    const handleChange = (e) => {
        setSelectedSportsbooks(Array.isArray(e) ? e.map((x) => x.value) : []); // && e.length > 0 -- options.map((o) => o.value
    };

    const columnParams = {
        player: true,
        single_outcome_type: false,
        outcome_types: [
            {
                line: false,
                title: 'yes'
            }
        ]
    };

    return(
        <section>
            <Select
                isMulti
                Placeholder="Select sportsbooks"
                options={options}
                onChange={handleChange}
                isSearchable
                value={options.filter((o) => selectedSportsbooks.includes(o.value))}//(options.filter((o) => selectedSportsbooks.includes(o.value)))}
            />
            <TabulatorOutcomeTable
                data={PROPS_DATA}
                column_params={columnParams}
                watchlist='false'
                prop_type='player'
                outcome_type_count='1'
                outcome_types="YesNo"
                outcome_type_1="Yes"
                sportsbooks={selectedSportsbooks}
            />
            {betslipCtx.showModal && <Betslip />}
        </section>
    );
}

export default PlayerPropsYesNo;