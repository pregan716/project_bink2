import React, { useState, useRef, useContext } from "react";
import { useNavigate } from 'react-router-dom';
import AuthContext from '../../store/auth-context';


const AuthForm = (props) =>  {
  
    const authCtx = useContext(AuthContext);
    const usernameInputRef = useRef();
    const passwordInputRef = useRef();
  
    const [error, setError] = useState(null);

    const navigate = useNavigate();

    const login = (event) => {
        event.preventDefault();
        fetch("http://localhost:8000/api/login/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": props.token,
          },
          credentials: "include",
          body: JSON.stringify({username: usernameInputRef.current.value, password: passwordInputRef.current.value}),
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
          //setAuthenticated(true); // TODO: delete if code works without this
          authCtx.login();
          authCtx.getCSRF();
          navigate("/");
        })
        .catch((err) => {
          console.log(err);
          setError("Wrong username or password.");
        });
      }

    return (
        <div className="container mt-3">
            <div>
                <h2>Login</h2>
                <form onSubmit={login}>
                    <div className="form-group">
                    <label htmlFor="username">Username</label>
                    <input type="text" className="form-control" id="username" name="username" required ref={usernameInputRef} />
                    </div>
                    <div className="form-group">
                    <label htmlFor="password">Password</label>
                    <input type="password" className="form-control" id="password" name="password" required ref={passwordInputRef} />
                    <div>
                        {error &&
                        <small className="text-danger">
                            {error}
                        </small>
                        }
                    </div>
                    </div>
                    <button type="submit" className="btn btn-primary">Login</button>
                </form>
            </div>
        </div>
    );
}


export default AuthForm;