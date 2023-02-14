import React, { useState, useEffect } from 'react';

const AuthContext = React.createContext({
    isLoggedIn: false,
    username: '',
    accountBalance: 0,
    csrfToken: null,
    login: () => {},
    logout: () => {},
    getSession: () => {},
    setCSRF: () => {},
    getCSRF: () => {},
    updateBalance: () => {},
}); 


export const AuthContextProvider = (props) => {

    const [userIsLoggedIn, setUserLoggedIn] = useState(false);
    const [userName, setUserName] = useState('');
    const [accountBalance, setAccountBalance] = useState(0.00);
    const [csrf, setCSRF] = useState(null);
    
    
    useEffect(() => {
        fetch("http://localhost:8000/api/session/", {
            credentials: "include",
        })
        .then((res) => res.json())
        .then((data) => {
            console.log(data);
        if (data.isAuthenticated) {
            loginHandler();
            getCSRFHandler();
        } else {
            setUserLoggedIn(false);
            setUserName('');
            getCSRFHandler();
        }})
        .catch((err) => {
            console.log(err);
        });
    }, []);


    const getSessionHandler = () => {
        fetch("http://localhost:8000/api/session/", {
            credentials: "include",
        })
        .then((res) => res.json())
        .then((data) => {
            console.log(data);
        if (data.isAuthenticated) {
            loginHandler();
        } else {
            setUserLoggedIn(false);
            setUserName('');
            getCSRFHandler();
        }})
        .catch((err) => {
            console.log(err);
        });
    }


    const whoami = () => {
        fetch("http://localhost:8000/api/whoami/", {
        headers: {
            "Content-Type": "application/json",
        },
            credentials: "include",
        })
        .then((res) => res.json())
        .then((data) => {
            console.log('whoami');
            setUserName(data.username);
            setAccountBalance(data.account_balance);
        })
        .catch((err) => {
            console.log(err);
        });
    }

    const logoutHandler = () => {
        fetch("http://localhost:8000/api/logout", {
        credentials: "include",
        })
        .then((response) => {
            if (response.status >= 200 && response.status <= 299) {
                response.json();
            } else {
                console.log(response.statusText);
                throw Error(response.statusText);
            }
        })
        .then((data) => {
            console.log(data);
            setUserLoggedIn(false);
            setUserName('');
        })
        .catch((err) => {
            console.log(err);
        });
    };

    const loginHandler = () => {
        setUserLoggedIn(true);
        setUserName(whoami());
    }


    const logoutHandler_old = () => {
        setUserLoggedIn(false);
        setUserName('');
    }

    const getCSRFHandler = () => {
        fetch("http://localhost:8000/api/csrf/", {
            credentials: "include",
        })
        .then((res) => {
            let csrfToken = res.headers.get("X-CSRFToken");
            setCSRF(csrfToken);
        })
        .catch((err) => {
            console.log(err);
        });
    }

    const setCSRFHandler = (token) => {
        if (token !== null) {
            setCSRF(token);
        }
    }

    const updateBalanceHandler = (balance) => {
        if (balance !== null) {
            setAccountBalance(balance);
        }
    }
    

    const contextValue = {
        isLoggedIn: userIsLoggedIn,
        username: userName,
        accountBalance: accountBalance,
        csrfToken: csrf,
        login: loginHandler,
        logout: logoutHandler,
        setCSRF: setCSRFHandler,
        getCSRF: getCSRFHandler,
        updateBalance: updateBalanceHandler,
        getSession: getSessionHandler,
    };
    
    return (
        <AuthContext.Provider value={contextValue}>
        {props.children}
        </AuthContext.Provider>
    );
};

export default AuthContext;