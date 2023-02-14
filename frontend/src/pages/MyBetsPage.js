import React, { useState, useEffect } from "react";
import MyBetsTable from "../components/MyBetsTable";
import axios from "axios";
import { 
    Nav,
    NavLink,
    NavItem,
    TabContent,
    TabPane,
    Row,
    Col,
} from "reactstrap";
import classnames from 'classnames';


function MyBetsPage (props) {
    
    // State variables
    const [isLoading, setLoading] = useState(true);
    const [OPEN_BETS, setOpenBets] = useState();
    const [CLOSED_BETS, setClosedBets] = useState();
    const [currentActiveTab, setCurrentActiveTab] = useState('1');

    // Toggle active state for Tab
    const toggle = tab => {
        if (currentActiveTab !== tab) setCurrentActiveTab(tab);
    }
    
    // Call user bets API
    useEffect(() => {
        setLoading(true);
        axios
        .get("/oddsapi/userbets")
        .then((response) => {
            return response.data;
        })
        .then((data) => {
            const open_bets = [];
            const closed_bets = [];

            for (const key in data) {
            const bet = {
                id: key,
                ...data[key],
            };
            if (bet.is_win === null) {
                open_bets.push(bet);
            }
            else {
                closed_bets.push(bet);
            }
        }
            setLoading(false);
            setOpenBets(open_bets);
            setClosedBets(closed_bets);
        })
    }, []);

    
    // Loading message
    if (isLoading) {
        return <div className="App">Loading...</div>;
    }

    
    // Return JSX component
    return(
        <React.Fragment>
            <Nav tabs>
                <NavItem>
                    <NavLink
                        className={classnames({
                            active:
                                currentActiveTab === '1'
                        })}
                        onClick={() => { toggle('1'); }}
                    >
                        Open bets 
                    </NavLink>
                </NavItem>
                <NavItem>
                    <NavLink
                        className={classnames({
                            active:
                                currentActiveTab === '2'
                        })}
                        onClick={() => { toggle('2'); }}
                    >
                        Closed bets
                    </NavLink>
                </NavItem>
            </Nav>
            <TabContent activeTab={currentActiveTab}>
                <TabPane tabId="1">
                    <Row>
                        <Col sm="12">
                            {OPEN_BETS.length === 0 && (
                                <h4>You have no open bets</h4>
                            )}
                            {OPEN_BETS.length > 0 && (
                                <MyBetsTable
                                    data={OPEN_BETS}
                                />
                            )}
                        </Col>
                    </Row>
                </TabPane>
                <TabPane tabId="2">
                    <Row>
                        <Col sm="12">
                        {CLOSED_BETS.length === 0 && (
                                <h4>You have no closed bets</h4>
                        )}
                        {CLOSED_BETS.length > 0 && (
                            <MyBetsTable
                                data={CLOSED_BETS}
                            />
                        )}
                        </Col>
                    </Row>
                </TabPane>
            </TabContent>
        </React.Fragment>
    );

}

export default MyBetsPage;