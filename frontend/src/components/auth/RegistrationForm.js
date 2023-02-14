import React, { useState, useRef, useContext } from "react";
import { useNavigate } from 'react-router-dom';
import AuthContext from '../../store/auth-context';


const RegistrationForm = (props) =>  {
  
    const authCtx = useContext(AuthContext);

    const usernameRegInputRef = useRef();
    const passwordRegInputRef = useRef();
    const confirmationRegInputRef = useRef();
  
    const [error, setError] = useState(null);

    const navigate = useNavigate();

    const register = (event) => {

        console.log('start registration');
        console.log(props.token);
        event.preventDefault();
        fetch("http://localhost:8000/api/register/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": props.token,
        },
        credentials: "include",
        body: JSON.stringify({username: usernameRegInputRef.current.value, password: passwordRegInputRef.current.value, confirmation: confirmationRegInputRef.current.value}),
        })
        .then((response) => {
            if (response.status >= 200 && response.status <= 299) {
                return response.json();
            } else {
                throw Error(response.statusText);
            }
        })
        .then((data) => {
            console.log(data);
            authCtx.login();
            navigate("/");
        })
        .catch((err) => {
            console.log(err);
            setError(err);
        });
    };

    return (
        <div className="container mt-3">
            <h2>Register</h2>
            <form onSubmit={register}>
                <div className="form-group">
                    <label htmlFor="username">Username</label>
                    <input type="text" className="form-control" id="reg_username" name="reg_username" required ref={usernameRegInputRef} />
                </div>
                <div className="form-group">
                    <label htmlFor="password">Password</label>
                    <input type="password" className="form-control" id="reg_password" name="reg_password" required ref={passwordRegInputRef} />
                </div>
                <div className="form-group">
                    <label htmlFor="confirmation">Confirm password</label>
                    <input type="password" className="form-control" id="reg_confirmation" name="reg_confirmation" required ref={confirmationRegInputRef} />
                </div>
                <div>
                    {error &&
                    <small className="text-danger">
                        {error}
                    </small>
                    }
                </div>
                <button type="submit" className="btn btn-primary">Register</button>
            </form>
        </div>
    );
}


export default RegistrationForm;