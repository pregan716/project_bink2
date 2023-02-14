import React from "react";
import { NumericFormat } from 'react-number-format';

const Currency = (props) => {
    return <NumericFormat value={props.value} displayType={'text'} thousandSeparator={true} prefix={'$'} />
}

export default Currency;