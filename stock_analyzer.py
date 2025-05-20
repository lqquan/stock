import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import requests
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
import logging

class StockAnalyzer:
    def __init__(self, initial_cash=1000000):
        # 设置日志
        logging.basicConfig(level=logging.INFO,
                          format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # 加载环境变量
        load_dotenv()
        
        # 配置参数
        self.params = {
            'ma_periods': {'short': 5, 'medium': 20, 'long': 60},
            'rsi_period': 14,
            'bollinger_period': 20,
            'bollinger_std': 2,
            'volume_ma_period': 20,
            'atr_period': 14,
            'stochastic_k': 14,
            'stochastic_d': 3,
            'cci_period': 20,
            'adx_period': 14,
            'ichimoku': {'tenkan': 9, 'kijun': 26, 'senkou_span_b': 52},
            'mfi_period': 14,
            'std_dev_period': 20,
            'z_score_period': 20
        }
        
    def get_stock_data(self, stock_code, start_date=None, end_date=None):
        """获取股票数据"""
        import akshare as ak
        
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
            
        try:
            # 使用 akshare 获取股票数据
            df = ak.stock_zh_a_hist(symbol=stock_code, 
                                  start_date=start_date, 
                                  end_date=end_date,
                                  adjust="qfq")
            
            # 重命名列名以匹配分析需求
            df = df.rename(columns={
                "日期": "date",
                "开盘": "open",
                "收盘": "close",
                "最高": "high",
                "最低": "low",
                "成交量": "volume"
            })
            
            # 确保日期格式正确
            df['date'] = pd.to_datetime(df['date'])
            
            # 数据类型转换
            numeric_columns = ['open', 'close', 'high', 'low', 'volume']
            df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')
            
            # 删除空值
            df = df.dropna()
            
            return df.sort_values('date')
            
        except Exception as e:
            self.logger.error(f"获取股票数据失败: {str(e)}")
            raise Exception(f"获取股票数据失败: {str(e)}")
            
    def calculate_ema(self, series, period):
        """计算指数移动平均线"""
        return series.ewm(span=period, adjust=False).mean()
        
    def calculate_rsi(self, series, period):
        """计算RSI指标"""
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
        
    def calculate_macd(self, series):
        """计算MACD指标"""
        exp1 = series.ewm(span=12, adjust=False).mean()
        exp2 = series.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        hist = macd - signal
        return macd, signal, hist
        
    def calculate_bollinger_bands(self, series, period, std_dev):
        """计算布林带"""
        middle = series.rolling(window=period).mean()
        std = series.rolling(window=period).std()
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        return upper, middle, lower
        
    def calculate_atr(self, df, period):
        """计算ATR指标"""
        high = df['high']
        low = df['low']
        close = df['close'].shift(1)
        
        tr1 = high - low
        tr2 = abs(high - close)
        tr3 = abs(low - close)
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()
        
    def calculate_stochastic(self, df, k_period, d_period):
        """计算随机震荡指标(Stochastic Oscillator)"""
        high_roll = df['high'].rolling(window=k_period).max()
        low_roll = df['low'].rolling(window=k_period).min()
        k = 100 * (df['close'] - low_roll) / (high_roll - low_roll)
        d = k.rolling(window=d_period).mean()
        return k, d
        
    def calculate_cci(self, df, period):
        """计算顺势指标(CCI)"""
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        mean_tp = typical_price.rolling(window=period).mean()
        mean_deviation = abs(typical_price - mean_tp).rolling(window=period).mean()
        cci = (typical_price - mean_tp) / (0.015 * mean_deviation)
        return cci
        
    def calculate_adx(self, df, period):
        """计算平均趋向指数(ADX)"""
        tr = self.calculate_tr(df)
        up_move = df['high'].diff()
        down_move = df['low'].diff(-1).abs()
        
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
        
        plus_di = 100 * pd.Series(plus_dm).rolling(window=period).mean() / tr.rolling(window=period).mean()
        minus_di = 100 * pd.Series(minus_dm).rolling(window=period).mean() / tr.rolling(window=period).mean()
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        return adx, plus_di, minus_di
        
    def calculate_tr(self, df):
        """计算真实波幅(True Range)"""
        high = df['high']
        low = df['low']
        close_prev = df['close'].shift(1)
        
        tr1 = high - low
        tr2 = abs(high - close_prev)
        tr3 = abs(low - close_prev)
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr
        
    def calculate_ichimoku(self, df, tenkan_period, kijun_period, senkou_span_b_period):
        """计算一目均衡表(Ichimoku Cloud)"""
        # 转换线(Tenkan-sen)
        tenkan_high = df['high'].rolling(window=tenkan_period).max()
        tenkan_low = df['low'].rolling(window=tenkan_period).min()
        tenkan_sen = (tenkan_high + tenkan_low) / 2
        
        # 基准线(Kijun-sen)
        kijun_high = df['high'].rolling(window=kijun_period).max()
        kijun_low = df['low'].rolling(window=kijun_period).min()
        kijun_sen = (kijun_high + kijun_low) / 2
        
        # 先行带A(Senkou Span A)
        senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(kijun_period)
        
        # 先行带B(Senkou Span B)
        senkou_b_high = df['high'].rolling(window=senkou_span_b_period).max()
        senkou_b_low = df['low'].rolling(window=senkou_span_b_period).min()
        senkou_span_b = ((senkou_b_high + senkou_b_low) / 2).shift(kijun_period)
        
        # 延迟线(Chikou Span)
        chikou_span = df['close'].shift(-kijun_period)
        
        return tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span
        
    def calculate_obv(self, df):
        """计算能量潮(OBV)"""
        obv = np.zeros(len(df))
        for i in range(1, len(df)):
            if df['close'].iloc[i] > df['close'].iloc[i-1]:
                obv[i] = obv[i-1] + df['volume'].iloc[i]
            elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                obv[i] = obv[i-1] - df['volume'].iloc[i]
            else:
                obv[i] = obv[i-1]
        return pd.Series(obv, index=df.index)
        
    def calculate_mfi(self, df, period):
        """计算资金流量指标(MFI)"""
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        raw_money_flow = typical_price * df['volume']
        
        positive_flow = np.where(typical_price > typical_price.shift(1), raw_money_flow, 0)
        negative_flow = np.where(typical_price < typical_price.shift(1), raw_money_flow, 0)
        
        positive_flow_sum = pd.Series(positive_flow).rolling(window=period).sum()
        negative_flow_sum = pd.Series(negative_flow).rolling(window=period).sum()
        
        money_ratio = positive_flow_sum / negative_flow_sum
        mfi = 100 - (100 / (1 + money_ratio))
        
        return mfi
        
    def calculate_standard_deviation(self, series, period):
        """计算标准差"""
        return series.rolling(window=period).std()
        
    def calculate_z_score(self, series, period):
        """计算Z-Score"""
        mean = series.rolling(window=period).mean()
        std = series.rolling(window=period).std()
        return (series - mean) / std
        
    def calculate_indicators(self, df):
        """计算技术指标"""
        try:
            # 📊 一、趋势类指标（Trend Indicators）
            # MA（Moving Average）移动平均线
            df['SMA5'] = df['close'].rolling(window=self.params['ma_periods']['short']).mean()
            df['SMA20'] = df['close'].rolling(window=self.params['ma_periods']['medium']).mean()
            df['SMA60'] = df['close'].rolling(window=self.params['ma_periods']['long']).mean()
            df['EMA5'] = self.calculate_ema(df['close'], self.params['ma_periods']['short'])
            df['EMA20'] = self.calculate_ema(df['close'], self.params['ma_periods']['medium'])
            df['EMA60'] = self.calculate_ema(df['close'], self.params['ma_periods']['long'])
            
            # MACD（移动平均收敛/发散指标）
            df['MACD'], df['Signal'], df['MACD_hist'] = self.calculate_macd(df['close'])
            
            # Bollinger Bands（布林带）
            df['BB_upper'], df['BB_middle'], df['BB_lower'] = self.calculate_bollinger_bands(
                df['close'],
                self.params['bollinger_period'],
                self.params['bollinger_std']
            )
            
            # ADX（平均趋向指数）
            df['ADX'], df['DI+'], df['DI-'] = self.calculate_adx(df, self.params['adx_period'])
            
            # Ichimoku Cloud（一目均衡表）
            df['Tenkan'], df['Kijun'], df['Senkou_A'], df['Senkou_B'], df['Chikou'] = self.calculate_ichimoku(
                df,
                self.params['ichimoku']['tenkan'],
                self.params['ichimoku']['kijun'],
                self.params['ichimoku']['senkou_span_b']
            )
            
            # ⚡ 二、动量类指标（Momentum Indicators）
            # RSI（相对强弱指标）
            df['RSI'] = self.calculate_rsi(df['close'], self.params['rsi_period'])
            
            # Stochastic Oscillator（随机震荡指标）
            df['Stoch_K'], df['Stoch_D'] = self.calculate_stochastic(
                df, 
                self.params['stochastic_k'],
                self.params['stochastic_d']
            )
            
            # CCI（顺势指标）
            df['CCI'] = self.calculate_cci(df, self.params['cci_period'])
            
            # ROC（变动率指标）
            df['ROC'] = df['close'].pct_change(periods=10) * 100
            
            # 💹 三、成交量类指标（Volume Indicators）
            # OBV（能量潮）
            df['OBV'] = self.calculate_obv(df)
            
            # VOL（成交量）
            df['Volume_MA'] = df['volume'].rolling(window=self.params['volume_ma_period']).mean()
            df['Volume_Ratio'] = df['volume'] / df['Volume_MA']
            
            # MFI（资金流量指标）
            df['MFI'] = self.calculate_mfi(df, self.params['mfi_period'])
            
            # 🧠 四、波动率类指标（Volatility Indicators）
            # ATR（平均真实波幅）
            df['ATR'] = self.calculate_atr(df, self.params['atr_period'])
            df['Volatility'] = df['ATR'] / df['close'] * 100
            
            # Standard Deviation（标准差）
            df['StdDev'] = self.calculate_standard_deviation(df['close'], self.params['std_dev_period'])
            
            # 🧮 五、统计套利类指标
            # Z-Score
            df['Z-Score'] = self.calculate_z_score(df['close'], self.params['z_score_period'])
            
            return df
            
        except Exception as e:
            self.logger.error(f"计算技术指标时出错: {str(e)}")
            raise
            
    def calculate_score(self, df):
        """计算股票评分 - 更加详细和精确的评分系统"""
        try:
            score = 0
            score_details = {}
            latest = df.iloc[-1]
            
            # 1. 📊 趋势评分 (40分)
            trend_score = 0
            
            # 1.1 移动平均线多头排列 (15分)
            if latest['EMA5'] > latest['EMA20'] > latest['EMA60']:
                trend_score += 15
                score_details['ma_alignment'] = '多头排列 +15'
            elif latest['EMA5'] < latest['EMA20'] < latest['EMA60']:
                score_details['ma_alignment'] = '空头排列 +0'
            else:
                # 部分多头特征加5分
                if latest['EMA5'] > latest['EMA20']:
                    trend_score += 5
                    score_details['ma_alignment'] = '部分多头特征 +5'
                else:
                    score_details['ma_alignment'] = '无明显排列 +0'
            
            # 1.2 MACD信号 (10分)
            if latest['MACD'] > latest['Signal'] and latest['MACD_hist'] > 0:
                # MACD金叉且柱状体为正
                trend_score += 10
                score_details['macd'] = '金叉且柱状体为正 +10'
            elif latest['MACD'] > latest['Signal']:
                # 仅MACD金叉
                trend_score += 5
                score_details['macd'] = '金叉 +5'
            elif latest['MACD'] < latest['Signal'] and latest['MACD_hist'] < 0:
                score_details['macd'] = '死叉且柱状体为负 +0'
            else:
                score_details['macd'] = '死叉 +0'
            
            # 1.3 ADX强度 (10分)
            if latest['ADX'] > 30:
                # 强势趋势
                trend_score += 10
                score_details['adx'] = f'强势趋势({latest["ADX"]:.1f}) +10'
            elif latest['ADX'] > 20:
                # 中等趋势
                trend_score += 5
                score_details['adx'] = f'中等趋势({latest["ADX"]:.1f}) +5'
            else:
                score_details['adx'] = f'弱势趋势({latest["ADX"]:.1f}) +0'
            
            # 1.4 布林带位置 (5分)
            if latest['close'] > latest['BB_middle'] and latest['close'] < latest['BB_upper']:
                # 上轨区域但不超买
                trend_score += 5
                score_details['bollinger'] = '上轨区域 +5'
            elif latest['close'] < latest['BB_middle'] and latest['close'] > latest['BB_lower']:
                # 下轨区域但不超卖
                trend_score += 2
                score_details['bollinger'] = '下轨区域 +2'
            elif latest['close'] > latest['BB_upper']:
                # 超过上轨(超买)不加分
                score_details['bollinger'] = '超买区域 +0'
            else:
                # 超过下轨(超卖)不加分
                score_details['bollinger'] = '超卖区域 +0'
            
            # 2. ⚡ 动量评分 (25分)
            momentum_score = 0
            
            # 2.1 RSI (10分)
            if 40 <= latest['RSI'] <= 60:
                # 中性区域，增长空间
                momentum_score += 10
                score_details['rsi'] = f'中性({latest["RSI"]:.1f}) +10'
            elif 30 <= latest['RSI'] < 40 or 60 < latest['RSI'] <= 70:
                # 偏离中性但未到极值
                momentum_score += 5
                score_details['rsi'] = f'偏离中性({latest["RSI"]:.1f}) +5'
            elif latest['RSI'] < 30:
                # 超卖区域，不鼓励盲目抄底
                momentum_score += 2
                score_details['rsi'] = f'超卖({latest["RSI"]:.1f}) +2'
            else:
                # 超买区域，不鼓励追高
                score_details['rsi'] = f'超买({latest["RSI"]:.1f}) +0'
            
            # 2.2 随机震荡指标KD (5分)
            if latest['Stoch_K'] < latest['Stoch_D'] and 20 <= latest['Stoch_K'] <= 80:
                momentum_score += 5
                score_details['kd'] = f'K({latest["Stoch_K"]:.1f})低于D({latest["Stoch_D"]:.1f})且在合理区间 +5'
            elif latest['Stoch_K'] > latest['Stoch_D'] and 20 <= latest['Stoch_K'] <= 80:
                momentum_score += 3
                score_details['kd'] = f'K({latest["Stoch_K"]:.1f})高于D({latest["Stoch_D"]:.1f})且在合理区间 +3'
            else:
                score_details['kd'] = f'K({latest["Stoch_K"]:.1f})和D({latest["Stoch_D"]:.1f})关系不佳或超出合理区间 +0'
            
            # 2.3 CCI (5分)
            if -100 <= latest['CCI'] <= 100:
                momentum_score += 5
                score_details['cci'] = f'处于正常区间({latest["CCI"]:.1f}) +5'
            elif -200 <= latest['CCI'] < -100:
                momentum_score += 2
                score_details['cci'] = f'偏弱({latest["CCI"]:.1f}) +2'
            elif 100 < latest['CCI'] <= 200:
                momentum_score += 2
                score_details['cci'] = f'偏强({latest["CCI"]:.1f}) +2'
            else:
                score_details['cci'] = f'极端区域({latest["CCI"]:.1f}) +0'
            
            # 2.4 ROC变动率 (5分)
            if 0 < latest['ROC'] <= 5:
                momentum_score += 5
                score_details['roc'] = f'适中正增长({latest["ROC"]:.1f}%) +5'
            elif -5 <= latest['ROC'] < 0:
                momentum_score += 2
                score_details['roc'] = f'轻微下跌({latest["ROC"]:.1f}%) +2'
            elif 5 < latest['ROC'] <= 10:
                momentum_score += 2
                score_details['roc'] = f'较快增长({latest["ROC"]:.1f}%), 风险增加 +2'
            else:
                score_details['roc'] = f'极端变化({latest["ROC"]:.1f}%) +0'
            
            # 3. 💹 成交量评分 (20分)
            volume_score = 0
            
            # 3.1 成交量变化 (10分)
            if 1.0 <= latest['Volume_Ratio'] <= 2.0:
                # 成交量适度放大
                volume_score += 10
                score_details['volume'] = f'适度放大({latest["Volume_Ratio"]:.1f}) +10'
            elif 0.5 <= latest['Volume_Ratio'] < 1.0:
                # 略低但可接受
                volume_score += 5
                score_details['volume'] = f'略低但可接受({latest["Volume_Ratio"]:.1f}) +5'
            elif latest['Volume_Ratio'] > 2.0:
                # 过度放量可能暗示风险
                volume_score += 2
                score_details['volume'] = f'过度放量({latest["Volume_Ratio"]:.1f}) +2'
            else:
                score_details['volume'] = f'成交低迷({latest["Volume_Ratio"]:.1f}) +0'
            
            # 3.2 OBV趋势 (5分)
            obv_trend = self._get_obv_trend(df)
            if obv_trend == "上升":
                volume_score += 5
                score_details['obv'] = f'上升趋势 +5'
            elif obv_trend == "横盘":
                volume_score += 2
                score_details['obv'] = f'横盘整理 +2'
            else:
                score_details['obv'] = f'下降趋势 +0'
            
            # 3.3 MFI资金流向 (5分)
            if 40 <= latest['MFI'] <= 60:
                volume_score += 5
                score_details['mfi'] = f'中性资金流({latest["MFI"]:.1f}) +5'
            elif 20 <= latest['MFI'] < 40 or 60 < latest['MFI'] <= 80:
                volume_score += 3
                score_details['mfi'] = f'偏离中性({latest["MFI"]:.1f}) +3'
            else:
                score_details['mfi'] = f'极端区域({latest["MFI"]:.1f}) +0'
            
            # 4. 🧠 波动率评分 (10分)
            volatility_score = 0
            
            # 4.1 ATR与价格比率 (5分)
            if latest['Volatility'] <= 2:
                volatility_score += 5
                score_details['volatility'] = f'低波动({latest["Volatility"]:.1f}%) +5'
            elif latest['Volatility'] <= 4:
                volatility_score += 3
                score_details['volatility'] = f'中等波动({latest["Volatility"]:.1f}%) +3'
            else:
                score_details['volatility'] = f'高波动({latest["Volatility"]:.1f}%) +0'
            
            # 4.2 价格标准差 (5分)
            if latest['StdDev'] / latest['close'] * 100 <= 3:
                volatility_score += 5
                score_details['std_dev'] = f'低离散度({latest["StdDev"]:.2f}) +5'
            elif latest['StdDev'] / latest['close'] * 100 <= 6:
                volatility_score += 3
                score_details['std_dev'] = f'中等离散度({latest["StdDev"]:.2f}) +3'
            else:
                score_details['std_dev'] = f'高离散度({latest["StdDev"]:.2f}) +0'
            
            # 5. 🧮 统计套利评分 (5分)
            stat_score = 0
            
            # 5.1 Z-Score均值回归可能性 (5分)
            if -2 <= latest['Z-Score'] <= 2:
                stat_score += 5
                score_details['z_score'] = f'合理区间({latest["Z-Score"]:.2f}) +5'
            elif -3 <= latest['Z-Score'] < -2 or 2 < latest['Z-Score'] <= 3:
                stat_score += 2
                score_details['z_score'] = f'边缘区域({latest["Z-Score"]:.2f}) +2'
            else:
                score_details['z_score'] = f'极端偏离({latest["Z-Score"]:.2f}) +0'
            
            # 汇总各部分得分
            score = trend_score + momentum_score + volume_score + volatility_score + stat_score
            
            # 汇总各类别得分
            category_scores = {
                'trend': trend_score,
                'momentum': momentum_score,
                'volume': volume_score,
                'volatility': volatility_score,
                'statistical': stat_score
            }
            
            return score, score_details, category_scores
            
        except Exception as e:
            self.logger.error(f"计算评分时出错: {str(e)}")
            raise
            
    def get_recommendation(self, score):
        """根据得分给出建议"""
        if score >= 75:
            return '推荐买入'
        elif score >= 60:
            return '建议关注'
        elif score >= 45:
            return '观望'
        elif score >= 30:
            return '建议减持'
        else:
            return '建议卖出'
            
    def analyze_stock(self, stock_code):
        """分析单个股票"""
        try:
            # 获取股票数据
            df = self.get_stock_data(stock_code)
            
            # 计算技术指标
            df = self.calculate_indicators(df)
            
            # 评分系统 - 获取详细得分
            score, score_details, category_scores = self.calculate_score(df)
            
            # 获取最新数据
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            # 生成报告
            report = {
                'stock_code': stock_code,
                'analysis_date': datetime.now().strftime('%Y-%m-%d'),
                'score': score,
                'score_details': score_details,
                'category_scores': category_scores,
                'price': latest['close'],
                'price_change': (latest['close'] - prev['close']) / prev['close'] * 100,
                
                # 趋势类指标
                'ma_trend': 'UP' if latest['EMA5'] > latest['EMA20'] else 'DOWN',
                'macd_signal': 'BUY' if latest['MACD'] > latest['Signal'] else 'SELL',
                'adx': latest['ADX'],
                'bb_position': self._get_bb_position(latest),
                
                # 动量类指标
                'rsi': latest['RSI'],
                'stoch_k': latest['Stoch_K'],
                'stoch_d': latest['Stoch_D'],
                'cci': latest['CCI'],
                'roc': latest['ROC'],
                
                # 成交量类指标
                'volume_status': 'HIGH' if latest['Volume_Ratio'] > 1.5 else 'NORMAL',
                'obv_trend': self._get_obv_trend(df),
                'mfi': latest['MFI'],
                
                # 波动率指标
                'atr': latest['ATR'],
                'volatility': latest['Volatility'],
                'std_dev': latest['StdDev'],
                
                # 统计类指标
                'z_score': latest['Z-Score'],
                
                # 支撑压力位
                'support_resistance': self._calculate_support_resistance(df),
                
                # 最终建议
                'recommendation': self.get_recommendation(score)
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"分析股票时出错: {str(e)}")
            raise
            
    def _get_bb_position(self, latest_row):
        """判断价格在布林带中的位置"""
        close = latest_row['close']
        upper = latest_row['BB_upper']
        middle = latest_row['BB_middle']
        lower = latest_row['BB_lower']
        
        if close > upper:
            return "上轨上方(超买)"
        elif close > middle:
            return "上轨区域"
        elif close < lower:
            return "下轨下方(超卖)"
        elif close < middle:
            return "下轨区域"
        else:
            return "中轨"
            
    def _get_obv_trend(self, df):
        """判断OBV趋势"""
        obv = df['OBV'].tail(5)
        if obv.iloc[-1] > obv.iloc[0]:
            return "上升"
        elif obv.iloc[-1] < obv.iloc[0]:
            return "下降"
        else:
            return "横盘"
            
    def _calculate_support_resistance(self, df):
        """计算支撑位和压力位"""
        try:
            # 获取最近的价格数据
            close = df['close'].tail(20)
            current_price = close.iloc[-1]
            
            # 计算波动范围
            price_range = df['high'].tail(20).max() - df['low'].tail(20).min()
            
            # 简单计算支撑位和压力位
            resistance = current_price + (price_range * 0.382)
            support = current_price - (price_range * 0.382)
            
            return f"支撑位: {support:.2f}, 压力位: {resistance:.2f}"
        except:
            return "无法计算支撑位和压力位"
            
    def scan_market(self, stock_list, min_score=60):
        """扫描市场，寻找符合条件的股票"""
        recommendations = []
        
        for stock_code in stock_list:
            try:
                report = self.analyze_stock(stock_code)
                if report['score'] >= min_score:
                    recommendations.append(report)
            except Exception as e:
                self.logger.error(f"分析股票 {stock_code} 时出错: {str(e)}")
                continue
                
        # 按得分排序
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations 