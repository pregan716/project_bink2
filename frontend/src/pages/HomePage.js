import { faAlignCenter } from "@fortawesome/free-solid-svg-icons";
import React, { useState, useEffect, useContext } from "react";
import MarketContext from "../store/market-context";

function HomePage(){
    const [player_prop_count, setPlayerPropCount] = useState();
    const [team_prop_count, setTeamPropCount] = useState();
    const [isLoading, setLoading] = useState(true);

    const marketCtx = useContext(MarketContext);

    useEffect(() => {
        setPlayerPropCount(marketCtx.player_props.length);
        setTeamPropCount(marketCtx.team_props.length);
    }, [marketCtx.player_props, marketCtx.team_props]);

    useEffect(() => {
        if (player_prop_count>0 || team_prop_count>0){
            setLoading(false);
        }
    }, [player_prop_count, team_prop_count]);

    const divstyle = {
        textAlign: 'center',
    }

    // Show temporary element until API call finishes
    if (isLoading) {
        return <div className="App">Loading...</div>;
    }

    return(
        <React.Fragment>
            <div style={divstyle}>
                <h3>Number of available markets</h3>
                <h4>Player props: {player_prop_count}</h4>
                <h4>Team props: {team_prop_count}</h4>
            </div>
        </React.Fragment>
    );

}

export default HomePage;