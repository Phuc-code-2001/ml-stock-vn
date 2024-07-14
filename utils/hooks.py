import streamlit as st

def use_state(key, init_value, return_reset=False):
    """
    A custom hook that allows you to create a state variable in Streamlit.
    This hook is inspired by React's useState hook.
    Parameters:
        key (str): The key of the state variable.
        init_value (any): The initial value of the state variable.
        return_reset (bool): If True, the hook will return a reset function.
    Returns:
        tuple: A tuple containing the getter, setter, and reset function (if return_reset=True).
    """
    if key not in st.session_state:
        st.session_state[key] = init_value

    if return_reset:
        return lambda: st.session_state[key], lambda x: st.session_state.update({key: x}), lambda: st.session_state.update({key: init_value})
    
    return lambda: st.session_state[key], lambda x: st.session_state.update({key: x})