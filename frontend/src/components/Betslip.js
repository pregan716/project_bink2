import React, { useState, useRef, useContext } from "react";
import { Modal, ModalHeader, ModalBody } from 'reactstrap';
import BetslipContext from "../store/betslip-context";
import classes from './Betslip.module.css';
import Currency from './auth/Currency';
import AuthContext from '../store/auth-context';



const Betslip = () =>  {
    const betslipCtx = useContext(BetslipContext);
    const wagerAmountInputRef = useRef(0);
    const authCtx = useContext(AuthContext);
    const [invalidWager, setInvalidWager] = useState(false);
    const [calculatedPayout, setCalculatedPayout] = useState(0);
    const [error, setError] = useState(null);
    
    const wagerChangeHandler = (event) => {
        if (betslipCtx.odds >= 100) {
            setCalculatedPayout(((betslipCtx.odds + 100) * event.target.value / 100).toFixed(2));
        }
        else if (betslipCtx.odds <= -100) {
            setCalculatedPayout((+event.target.value + +event.target.value / (-betslipCtx.odds / 100)).toFixed(2));
        }
        if ((+event.target.value > authCtx.accountBalance || +event.target.value <= 0) && (event.target.value !== '')) {
            setInvalidWager(true);
        }
        else {
            setInvalidWager(false);
        }
    }
    
    const placeBetHandler = (event) => {
        event.preventDefault();
        fetch("http://localhost:8000/api/place_bet/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": authCtx.csrfToken,
          },
          credentials: "include",
          body: JSON.stringify({value: betslipCtx.line, 
            payout_american: betslipCtx.odds,
            wager_amount: wagerAmountInputRef.current.value,
            market_outcome_type_id: betslipCtx.betting_market_outcome_type_id,
            outcome_ids: betslipCtx.outcome_ids,
        }),
        })
        .then((response) => response.json())
        .then((data) => {
          authCtx.updateBalance(+data.account_balance);
          betslipCtx.modalToggle();
        })
        .catch((err) => {
          console.log(err);
          setError("Error placing bet.");
        });
    }

    const cancelHandler = () => {
        betslipCtx.modalToggle();
    } 

    return (
        <div>
            <Modal isOpen={betslipCtx.showModal} toggle={betslipCtx.modalToggle} className={classes.modal} scrollable size='sm' >
                <ModalHeader toggle={betslipCtx.modalToggle}>Betslip</ModalHeader>
                <ModalBody>
                    <div className="container mt-3">
                        {betslipCtx.player!=null && <p><b>Player: </b>{betslipCtx.player}</p>}
                        <p><b>Game: </b>{betslipCtx.game}</p>
                        {betslipCtx.player===null && <p><b>Team: </b>{betslipCtx.team}</p>}
                        <p><b>Prop: </b>{betslipCtx.prop}</p>
                        <p><b>Side: </b>{betslipCtx.side}</p>
                        {betslipCtx.line!=null && <p><b>Line: </b>{betslipCtx.line}</p>}
                        <p><b>Odds: </b>{betslipCtx.odds}</p>
                        <form onSubmit={placeBetHandler}>
                            <div className="form-group">
                                <label htmlFor="wageramt">Wager:</label>
                                <input type="number" max={authCtx.accountBalance} min='0' className="form-control" id="wageramt" name="wageramt" style={{width: 100 + 'px'}} required ref={wagerAmountInputRef} onChange={wagerChangeHandler} />
                                {invalidWager &&
                                    <small className="text-danger">
                                        Wager must be greater than zero and cannot exceed account balance.
                                    </small>
                                }
                            </div>
                            <div>
                                <p>To pay out: <Currency value={calculatedPayout} /></p>
                            </div>
                            <button className="btn btn-light" onClick={cancelHandler}>Cancel</button>
                            <button type="submit" className="btn btn-primary" disabled={invalidWager}>Place bet</button>
                        </form>
                    </div>
                </ModalBody>
            </Modal>
        </div>
    );
}

export default Betslip;