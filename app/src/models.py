from sklearn.model_selection import TimeSeriesSplit
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import numpy as np
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import TimeSeriesSplit
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, Flatten, Dense
from tensorflow.keras.optimizers import Adam

class MojovaTool:
    def __init__(self):
        self.predictions = []
        self.actuals = []
        self.rmse = None
        self.overall_rmse = None
        self.future_prediction = None

    def randomforest(self, df, lagged_columns, target_column):

        X = df[lagged_columns]
        y = df[target_column]

        # Time-series split for backtesting
        tscv = TimeSeriesSplit(n_splits=7)

        for train_index, test_index in tscv.split(X):
            X_train, X_test = X.iloc[train_index], X.iloc[test_index]
            y_train, y_test = y.iloc[train_index], y.iloc[test_index]

            # Koulutetaan Random Forest Regressor
            model = RandomForestRegressor(n_estimators=6, random_state=42, max_depth=5, min_samples_split=2)
            model.fit(X_train, y_train)
            
            # Predict
            y_pred = model.predict(X_test)

            self.predictions.extend(y_pred)
            self. actuals.extend(y_test)
            
            # Evaluate performance on this fold
            self.rmse = np.sqrt(mean_squared_error(y_test, y_pred))


        self.overall_rmse = np.sqrt(mean_squared_error(self.actuals, self.predictions))

        # Train on the entire dataset and predict for the future
        last_observation = X.iloc[-1:]  # Extract the last observation
        self.future_prediction = model.predict(last_observation)[0]  # Predict the next value
        return self.future_prediction

    

    def cnn(self, model, lagged_features, lagged_columns, steps=5, new_budget=None, new_workforce=None):
        """
        CNN Model for Time Series Forecasting with Iterative Predictions using a Pre-trained Model.

        Args:
            model: Pre-trained Keras model.
            lagged_features: DataFrame containing lagged features.
            lagged_columns: List of columns used as predictors.
            steps: Number of future timesteps to predict iteratively.
            new_budget: Optional new value for 'quarterly_budget_lag1'.
            new_workforce: Optional new value for 'quarterly_workforce_lag1'.

        Returns:
            predictions: List of predicted values for multiple timesteps.
        """
        # Prepare Data
        columns_to_downscale = ['quarterly_budget_lag1', 'quarterly_workforce_lag1']
        lagged_features[columns_to_downscale] = np.log1p(lagged_features[columns_to_downscale]) / 2
        X = lagged_features[lagged_columns].values

        # Modify initial DataFrame with new values (if provided)
        if new_budget is not None:
            X[-1, lagged_columns.index('quarterly_budget_lag1')] = new_budget
        if new_workforce is not None:
            X[-1, lagged_columns.index('quarterly_workforce_lag1')] = new_workforce

        # Scale globally
        X_scaler = MinMaxScaler()
        X_scaled = X_scaler.fit_transform(X)

        # Start with the last observation
        last_X = X_scaled[-1:].reshape((1, 1, X_scaled.shape[1]))  # Shape: (1, 1, num_features)
        st.write(last_X.shape)

        predictions = []

        for step in range(steps):
            # Predict the next timestep
            pred_scaled = model.predict(last_X, verbose=0)

            # Append the prediction
            predictions.append(pred_scaled[0])

            # Prepare the next input: use the latest prediction
            pred_scaled = pred_scaled.reshape(1, 1, -1)  # Ensure correct shape
            st.write(pred_scaled.shape)
            last_X = np.concatenate([last_X[:, :, last_X.shape[2]:], pred_scaled], axis=2)  # Update input with new prediction
            st.write(last_X.shape)
        # Inverse scale the predictions back to the original scale
        predictions = X_scaler.inverse_transform(np.array(predictions))

        return predictions


    def plot_train_test():
        ...


    def plot_results(self):

        # Align lengths of actuals and predictions
        max_length = max(len(self.actuals), len(self.predictions) + 1)  # +1 to account for the future prediction

        # Pad actuals and predictions with None to match max_length
        actuals = list(self.actuals) + [None] * (max_length - len(self.actuals))
        predictions = list(self.predictions) + [None] * (max_length - len(self.predictions))
        predictions[-1] = self.future_prediction  # Add the future prediction as the last value

        # Create DataFrame for results
        results_df = pd.DataFrame({
            "Actual": actuals,
            "Predicted": predictions
        })

        # Plotly Figure
        fig = go.Figure()

        # Add actuals line
        fig.add_trace(go.Scatter(
            y=results_df["Actual"],
            mode="lines+markers",
            name="Todelliset Arvot",
            marker=dict(symbol="circle", size=8)
        ))

        # Add predictions line
        fig.add_trace(go.Scatter(
            y=results_df["Predicted"],
            mode="lines+markers",
            name="Ennustetut Arvot",
            marker=dict(symbol="x", size=8)
        ))

        # Update layout
        fig.update_layout(
            title="Tulokset: Todelliset Arvot vs Ennustetut Arvot",
            xaxis_title="Aikaindeksi",
            yaxis_title="Tyytyväisyys",
            legend_title="Selite",
            template="plotly_white",
            autosize=True,
            height=500,
        )

        # Show plot in Streamlit
        st.plotly_chart(fig, use_container_width=True)

    def plot_all_lines(self, *df, columns):
        kainuu_df, kooste_df = df

        st.write("Kainuu DataFrame:", kainuu_df.head())
        st.write("Kooste DataFrame:", kooste_df.head())
        for column in columns:
            fig = go.Figure()
            # Add Kainuu data
            fig.add_trace(go.Scatter(
                x=kainuu_df['quarter'], 
                y=kainuu_df[column],
                mode='lines+markers',
                name='Kainuu',
                marker=dict(symbol='circle')
            ))

            # Add Kooste data
            fig.add_trace(go.Scatter(
                x=kooste_df['quarter'], 
                y=kooste_df[column],
                mode='lines+markers',
                name='Kooste',
                marker=dict(symbol='x')
            ))

            # Update layout
            fig.update_layout(
                title=f"{column}",
                xaxis_title="Kvartaali",
                yaxis_title="Tyytyväisyys",
                legend_title="Ryhmät",
                template="plotly_white",
                height=500,
                autosize=True
            )


            st.plotly_chart(fig, use_container_width=True)
