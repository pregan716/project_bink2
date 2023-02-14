import React, { useState, useEffect, useContext } from 'react';
import AuthContext from './auth-context';
import axios from "axios";

const MarketContext = React.createContext({
    player_props: [],
    team_props: [],
    watchlist: [],
    edit_watchlist: () => {},
});

export const MarketContextProvider = (props) => {
    
    const authCtx = useContext(AuthContext);
    
    const [watchList, setWatchList] = useState([]);
    const [playerprops, setPlayerProps] = useState([]);
    const [teamprops, setTeamProps] = useState([]);

    useEffect(() => {
        if (authCtx.isLoggedIn === true) {
            get_watchlist();
        }
        else {
            setWatchList([]);
        }
    }, [authCtx.isLoggedIn]);

    // Call API to get market data
    useEffect(() => {
        axios
        .get("/oddsapi/market")
        .then((response) => {
            return response.data;
        })
        .then((data) => {
            const playerPropMarkets = [];
            const teamPropMarkets = [];

            for (const key in data) {
                const market = {
                    id: key,
                    ...data[key],
                };
                if (market.betting_market_type===2){
                    playerPropMarkets.push(market);
                }
                else if (market.betting_market_type===3){
                    teamPropMarkets.push(market);
            }
        }
            setPlayerProps(playerPropMarkets);
            setTeamProps(teamPropMarkets);
            console.log('mktctx useeffect');
            console.log(teamPropMarkets);
        })
    }, []);

    // Get watchlist and set state
    const get_watchlist = () => {
        fetch("http://localhost:8000/api/get_watchlist/", {
        headers: {
            "Content-Type": "application/json",
        },
            credentials: "include",
        })
        .then((res) => res.json())
        .then((data) => {
            console.log('get_watchlist');
            setWatchList(data.watchlist);
        })
        .catch((err) => {
            console.log(err);
        });
    }

    // Edit watchlist
    const editWatchlistHandler = (mot_id, csrf) => {
        console.log(authCtx.csrfToken);
        fetch("http://localhost:8000/api/edit_watchlist/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": authCtx.csrfToken,
        },
        credentials: "include",
        body: JSON.stringify({mot_id: mot_id}),
        })
        .then((response) => {
            if (response.status >= 200 && response.status <= 299) {
                response.json();
                //get_watchlist();
            } else {
                console.log(response.statusText);
                throw Error(response.statusText);
            }
        })
        .then((data) => {if (!watchList.includes(mot_id)) {
            const prevList = watchList;
            setWatchList([...prevList, mot_id]);
        } else {
            const newList = watchList.filter(item => item !== mot_id);
            setWatchList(newList);
        }})
        .catch((err) => {
        console.log(err);
        });
    }

    // Export context
    const contextValue = {
        player_props: playerprops,
        team_props: teamprops,
        watchlist: watchList,
        edit_watchlist: editWatchlistHandler,
    };
    
    return (
        <MarketContext.Provider value={contextValue}>
        {props.children}
        </MarketContext.Provider>
    );

}

export default MarketContext;