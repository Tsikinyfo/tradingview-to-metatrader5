# src/config/risk_config.py
from dataclasses import dataclass
from typing import Dict, Optional
import json
import os
import logging

logger = logging.getLogger('RiskConfig')

@dataclass
class RiskParameters:
    enabled: bool = False  # Toggle for risk management
    risk_percentage: float = 1.0  # Default 1% risk
    max_risk_per_trade: Optional[float] = None  # Optional max $ amount per trade
    min_position_size: Optional[float] = None  # Minimum position size

# Global risk parameters instance
RISK_CONFIG = RiskParameters()

# Path to save/load risk config
CONFIG_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                "config", "risk_config.json")

def save_config() -> None:
    """Save the current risk configuration to file"""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(CONFIG_FILE_PATH), exist_ok=True)
        
        # Convert to dict and save
        config_dict = {
            "enabled": RISK_CONFIG.enabled,
            "risk_percentage": RISK_CONFIG.risk_percentage,
            "max_risk_per_trade": RISK_CONFIG.max_risk_per_trade,
            "min_position_size": RISK_CONFIG.min_position_size
        }
        
        with open(CONFIG_FILE_PATH, 'w') as f:
            json.dump(config_dict, f, indent=2)
            
        logger.info(f"Risk configuration saved to {CONFIG_FILE_PATH}")
    except Exception as e:
        logger.error(f"Failed to save risk configuration: {e}")

def load_config() -> None:
    """Load risk configuration from file"""
    try:
        if os.path.exists(CONFIG_FILE_PATH):
            with open(CONFIG_FILE_PATH, 'r') as f:
                config_dict = json.load(f)
                
            # Update global config
            RISK_CONFIG.enabled = config_dict.get("enabled", False)
            RISK_CONFIG.risk_percentage = config_dict.get("risk_percentage", 1.0)
            RISK_CONFIG.max_risk_per_trade = config_dict.get("max_risk_per_trade")
            RISK_CONFIG.min_position_size = config_dict.get("min_position_size")
            
            logger.info(f"Risk configuration loaded from {CONFIG_FILE_PATH}")
        else:
            logger.info("No risk configuration file found, using defaults")
            # Create default config file for easy editing
            save_config()
    except Exception as e:
        logger.error(f"Failed to load risk configuration: {e}")

def get_risk_parameters() -> RiskParameters:
    """Get the current risk parameters"""
    return RISK_CONFIG

def get_risk_config_status() -> Dict:
    """Get the current risk configuration as a dictionary"""
    return {
        "enabled": RISK_CONFIG.enabled,
        "risk_percentage": RISK_CONFIG.risk_percentage,
        "max_risk_per_trade": RISK_CONFIG.max_risk_per_trade,
        "min_position_size": RISK_CONFIG.min_position_size
    }

# Load configuration on module import
load_config()