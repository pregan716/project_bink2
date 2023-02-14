import React, { useContext, useState, useEffect } from "react";
import 'react-tabulator/lib/css/tabulator.min.css'; // theme
import 'react-tabulator/lib/styles.css';
import axios from "axios";
import TabulatorOutcomeTable from "../components/TabulatorOutcomeTable";
import Select from "react-select";



function WatchlistPage(){
    

    // State attributes
    const [isLoading, setLoading] = useState(true);
    const [PROPS_DATA, setData] = useState([]);
    const [options, setOptions] = useState([]);
    const [selectedSportsbooks, setSelectedSportsbooks] = useState([]);

    // Call API to get market data
    useEffect(() => {
        setLoading(true);
        axios
        .get("/oddsapi/watchlist")
        .then((response) => {
            console.log('watchlist call');
            return response.data;
        })
        .then((data) => {
            const markets = [];

            for (const key in data) {
            const market = {
                id: key,
                ...data[key],
            };
            markets.push(market);
            }
            setData(markets);
            setSelectedSportsbooks(getBooks(markets));
            setLoading(false);
        })
    }, []);

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
        single_outcome_type: true,
        outcome_types: [
            {
                line: true,
                title: ''
            }
        ]
    };

    return(
        <div>
            {PROPS_DATA.length === 0 && (
                <h3>You do not have any bets in your watchlist.</h3>
            )}
            {PROPS_DATA.length > 0 && (
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
                        watchlist='true'
                        prop_type='player'
                        outcome_type_count='all'
                        outcome_types="OverUnder"
                        outcome_type_1="Over"
                        outcome_type_2="Under"
                        sportsbooks={selectedSportsbooks}
                    />
                </section>
            )}
        </div>
    );
}

export default WatchlistPage;