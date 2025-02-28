// frontend/src/reducers/hvacReducer.js
import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  data: [],
  loading: false,
  error: null,
  token: null,
  uuid: null,
  user: null,
};

const hvacSlice = createSlice({
  name: "user",
  initialState,
  reducers: {
    // ✅ Data fetching actions
    fetchDataRequest: (state) => {
      state.loading = true;
      state.error = null;
    },
    fetchDataSuccess: (state, action) => {
      state.loading = false;
      state.data = action.payload;
    },
    fetchDataFailure: (state, action) => {
      state.loading = false;
      state.error = action.payload;
    },

    // ✅ New user-related actions
    setUser: (state, action) => {
      state.token = action.payload.token;
      state.uuid = action.payload.uuid;
      state.user = action.payload;
      console.log("✅ Redux state updated:", state);
    },
    clearUser: (state) => {
      state.token = null;
      state.uuid = null;
    },
  },
});

export const {
  fetchDataRequest,
  fetchDataSuccess,
  fetchDataFailure,
  setUser,     // ✅ Export setUser action
  clearUser,   // ✅ Export clearUser action
} = hvacSlice.actions;

export default hvacSlice.reducer;