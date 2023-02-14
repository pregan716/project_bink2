import React, { useState, useContext, useEffect } from 'react';
import {
    Button,
    Collapse,
    Navbar,
    NavbarBrand,
    Nav,
    NavItem,
    NavLink,
    UncontrolledDropdown,
    DropdownToggle,
    DropdownMenu,
    DropdownItem,
} from 'reactstrap';
import classes from './MainNavigation.module.css';
import { useLocation, useNavigate } from 'react-router-dom';
import AuthContext from '../../store/auth-context';
import Currency from '../auth/Currency';

function MainNavigation(){
    
    const authCtx = useContext(AuthContext);
    const [isAuthPath, setIsAuthPath] = useState(false);

    console.log('nav');
    console.log(authCtx.isLoggedIn);

    let location = useLocation();
    let path = location.pathname;

    useEffect(() => {
        if (path === '/auth'){
            setIsAuthPath(true);
        } else {
            setIsAuthPath(false);
        }
    }, [path]);

    
    const logout = () => {
        console.log('main nav logout call');
        authCtx.logout();
        nav('/');
    };

    const navigate = useNavigate();
    const nav = (path) => {
        navigate(path);
    }
    
    return (
        <div>
            <Navbar 
                expand="md"
                dark="true"
                color="dark"
            >
                <NavbarBrand className={classes.pointer} onClick={() => nav('/')}>Bink</NavbarBrand>
                <Collapse isOpen={true} navbar>
                    <Nav horizontal="center" navbar>
                        <UncontrolledDropdown nav inNavbar>
                            <DropdownToggle nav caret>
                                Player props
                            </DropdownToggle>
                            <DropdownMenu>
                                <DropdownItem className={classes.pointer} onClick={() => nav('/PlayerPropsOverUnder')}>Over / under</DropdownItem>
                                <DropdownItem className={classes.pointer} onClick={() => nav('/PlayerPropsYesNo')}>Yes / no</DropdownItem>
                            </DropdownMenu>
                        </UncontrolledDropdown>
                        <UncontrolledDropdown nav inNavbar>
                            <DropdownToggle nav caret>
                                Team props
                            </DropdownToggle>
                            <DropdownMenu>
                                <DropdownItem className={classes.pointer} onClick={() => nav('/TeamPropsOverUnder')}>Over / under</DropdownItem>
                                <DropdownItem className={classes.pointer} onClick={() => nav('/TeamPropsYesNo')}>Yes / no</DropdownItem>
                            </DropdownMenu>
                        </UncontrolledDropdown>
                        {authCtx.isLoggedIn && (
                            <React.Fragment>
                                <NavItem>
                                    <NavLink className={classes.pointer} onClick={() => nav('/watchlist')}>
                                        Watchlist
                                    </NavLink>
                                </NavItem>
                                <NavItem>
                                    <NavLink className={classes.pointer} onClick={() => nav('/mybets')}>
                                        My Bets
                                    </NavLink>
                                </NavItem>
                            </React.Fragment>
                        )}
                    </Nav>
                    <Nav className="ml-auto" pills>
                        
                        {authCtx.isLoggedIn && (
                            <React.Fragment>
                                <NavItem>
                                    <span className={classes.balance}>Balance: <Currency value={authCtx.accountBalance} /></span>
                                </NavItem>
                                <NavItem>
                                    <Button active onClick={logout}>
                                        Log out
                                    </Button>
                                </NavItem>
                            </React.Fragment>
                        )}

                        {!authCtx.isLoggedIn && !isAuthPath && (
                            <NavItem>
                                <Button active onClick={() => nav('/auth')}>
                                    Log in / Register
                                </Button>
                            </NavItem>
                        )}

                    </Nav>
                </Collapse>
            </Navbar>
        </div>
    );
}

export default MainNavigation;