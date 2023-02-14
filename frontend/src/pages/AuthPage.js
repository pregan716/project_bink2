import React, { useState, useEffect, useContext } from "react";
import { 
    Nav,
    NavLink,
    NavItem,
    TabContent,
    TabPane,
    Row,
    Col,
} from "reactstrap";
import AuthForm from '../components/auth/AuthForm';
import RegistrationForm from '../components/auth/RegistrationForm';
import classnames from 'classnames';
import AuthContext from "../store/auth-context";

function AuthPage(){

    const authCtx = useContext(AuthContext);

    const [currentActiveTab, setCurrentActiveTab] = useState('1');

    // Toggle active state for Tab
    const toggle = tab => {
        if (currentActiveTab !== tab) setCurrentActiveTab(tab);
    }

    useEffect(() => {
        console.log('auth form useEffect!');
        if (authCtx.isLoggedIn !== true){
            authCtx.getSession();
        }
    }, [authCtx.isLoggedIn]);

    return (
        <div>
            {authCtx.isLoggedIn && (
                <div>
                    <h2>You are logged in as { authCtx.username }</h2>
                </div>
            )}
            {!authCtx.isLoggedIn && (
                <div>
                    <Nav tabs>
                        <NavItem>
                            <NavLink
                                className={classnames({
                                    active:
                                        currentActiveTab === '1'
                                })}
                                onClick={() => { toggle('1'); }}
                            >
                                Log in  
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
                                Register
                            </NavLink>
                        </NavItem>
                    </Nav>
                    <TabContent activeTab={currentActiveTab}>
                        <TabPane tabId="1">
                            <Row>
                                <Col sm="12">
                                    <AuthForm token={authCtx.csrfToken} />
                                </Col>
                            </Row>
                        </TabPane>
                        <TabPane tabId="2">
                            <Row>
                                <Col sm="12">
                                    <RegistrationForm token={authCtx.csrfToken} />
                                </Col>
                            </Row>
                        </TabPane>
                    </TabContent>
                </div>
            )}
        </div>
    );
}

export default AuthPage;