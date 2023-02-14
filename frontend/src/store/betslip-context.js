import React, { useState } from 'react';

const BetslipContext = React.createContext({
    showModal: false,
    betting_market_outcome_type_id: '',
    player: '',
    team: '',
    game: '',
    prop: '',
    side: '',
    line: '',
    odds:'',
    outcome_ids: [],
    bet: () => {},
    modalToggle: () => {},
});


export const BetslipContextProvider = (props) => {
    
    
    const [showModal, setShowModal] = useState(false);
    const [bettingMarketOutcomeTypeID, setbettingMarketOutcomeTypeID] = useState();
    const [player, setPlayer] = useState();
    const [team, setTeam] = useState();
    const [game, setGame] = useState();
    const [prop, setProp] = useState();
    const [side, setSide] = useState();
    const [line, setLine] = useState();
    const [payout_american, setPayoutAmerican] = useState();
    const [betting_outcome_ids, setBettingOutcomeIDs] = useState([]);

    const betHandler = (cellData, ot_label) => {
        console.log('betslip bethandler');
        console.log(cellData);
        const outcome_type=cellData[ot_label + '_outcome_type'];
        if (cellData.market_type_id===2) {
            setPlayer(cellData.player);
        }
        else {
            setPlayer(null);
        }
        if (cellData[ot_label+"_best_line"]!='NA'){
            setLine(cellData[ot_label+"_best_line"]);
        }
        else{
            setLine(null);
        }
        setTeam(cellData.team);
        setGame(cellData.game);
        setProp(cellData.prop);
        setbettingMarketOutcomeTypeID(cellData[ot_label+"_betting_market_outcome_type_id"]);
        setSide(outcome_type);
        setPayoutAmerican(cellData[ot_label+"_best_odds"]);
        setBettingOutcomeIDs(cellData[ot_label+"_outcome_ids"]);
    }

    const modalToggleHandler = () => {
        console.log('betslip modaltoggle');
        let currentModal = showModal;
        console.log(!currentModal);
        setShowModal(!currentModal);
    }

    // Export context
    const contextValue = {
        showModal: showModal,
        betting_market_outcome_type_id: bettingMarketOutcomeTypeID,
        player: player,
        team: team,
        game: game,
        prop: prop,
        side: side,
        line: line,
        odds: payout_american,
        outcome_ids: betting_outcome_ids,
        bet: betHandler,
        modalToggle: modalToggleHandler,
    };
    
    return (
        <BetslipContext.Provider value={contextValue}>
        {props.children}
        </BetslipContext.Provider>
    );

}

export default BetslipContext;