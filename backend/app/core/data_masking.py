"""
PowerX 数据脱敏
创建日期: 2026-01-07
作者: zhi.qu

敏感数据脱敏处理
"""
import re
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from loguru import logger


class MaskType(str, Enum):
    """脱敏类型"""
    PHONE = "phone"           # 手机号
    ID_CARD = "id_card"       # 身份证
    BANK_CARD = "bank_card"   # 银行卡
    EMAIL = "email"           # 邮箱
    NAME = "name"             # 姓名
    ADDRESS = "address"       # 地址
    AMOUNT = "amount"         # 金额
    CUSTOM = "custom"         # 自定义


@dataclass
class MaskRule:
    """脱敏规则"""
    field_name: str
    mask_type: MaskType
    enabled: bool = True
    custom_func: Optional[Callable] = None


class DataMasker:
    """数据脱敏器"""
    
    def __init__(self):
        self._rules: Dict[str, MaskRule] = {}
        self._type_handlers: Dict[MaskType, Callable] = {
            MaskType.PHONE: self._mask_phone,
            MaskType.ID_CARD: self._mask_id_card,
            MaskType.BANK_CARD: self._mask_bank_card,
            MaskType.EMAIL: self._mask_email,
            MaskType.NAME: self._mask_name,
            MaskType.ADDRESS: self._mask_address,
            MaskType.AMOUNT: self._mask_amount,
        }
    
    def add_rule(self, rule: MaskRule):
        """添加脱敏规则"""
        self._rules[rule.field_name] = rule
    
    def remove_rule(self, field_name: str):
        """移除脱敏规则"""
        self._rules.pop(field_name, None)
    
    def mask_value(self, value: str, mask_type: MaskType) -> str:
        """脱敏单个值"""
        if not value:
            return value
        
        handler = self._type_handlers.get(mask_type)
        if handler:
            return handler(value)
        return value
    
    def mask_dict(self, data: Dict[str, Any], extra_rules: List[MaskRule] = None) -> Dict[str, Any]:
        """脱敏字典数据"""
        result = data.copy()
        
        # 合并规则
        rules = dict(self._rules)
        if extra_rules:
            for rule in extra_rules:
                rules[rule.field_name] = rule
        
        for field_name, rule in rules.items():
            if not rule.enabled:
                continue
            
            if field_name in result and result[field_name]:
                value = str(result[field_name])
                if rule.custom_func:
                    result[field_name] = rule.custom_func(value)
                else:
                    result[field_name] = self.mask_value(value, rule.mask_type)
        
        return result
    
    def mask_list(self, data_list: List[Dict], extra_rules: List[MaskRule] = None) -> List[Dict]:
        """脱敏列表数据"""
        return [self.mask_dict(item, extra_rules) for item in data_list]
    
    # 脱敏方法
    @staticmethod
    def _mask_phone(phone: str) -> str:
        """手机号脱敏: 138****1234"""
        if len(phone) >= 11:
            return phone[:3] + "****" + phone[-4:]
        return phone[:2] + "***"
    
    @staticmethod
    def _mask_id_card(id_card: str) -> str:
        """身份证脱敏: 110***********1234"""
        if len(id_card) >= 18:
            return id_card[:3] + "***********" + id_card[-4:]
        elif len(id_card) >= 15:
            return id_card[:3] + "********" + id_card[-4:]
        return "***"
    
    @staticmethod
    def _mask_bank_card(card: str) -> str:
        """银行卡脱敏: 6222 **** **** 1234"""
        digits = re.sub(r'\D', '', card)
        if len(digits) >= 16:
            return digits[:4] + " **** **** " + digits[-4:]
        return "**** " + digits[-4:] if len(digits) >= 4 else "****"
    
    @staticmethod
    def _mask_email(email: str) -> str:
        """邮箱脱敏: u***@example.com"""
        if "@" in email:
            parts = email.split("@")
            username = parts[0]
            domain = parts[1]
            if len(username) > 1:
                masked = username[0] + "***"
            else:
                masked = "***"
            return masked + "@" + domain
        return "***@***"
    
    @staticmethod
    def _mask_name(name: str) -> str:
        """姓名脱敏: 张*明 or 张**"""
        if len(name) == 2:
            return name[0] + "*"
        elif len(name) >= 3:
            return name[0] + "*" * (len(name) - 2) + name[-1]
        return "*"
    
    @staticmethod
    def _mask_address(address: str) -> str:
        """地址脱敏: 保留省市，其他脱敏"""
        # 简单处理：保留前10个字符，其余脱敏
        if len(address) > 10:
            return address[:10] + "***"
        return address[:len(address)//2] + "***"
    
    @staticmethod
    def _mask_amount(amount: str) -> str:
        """金额脱敏: 显示量级"""
        try:
            num = float(amount.replace(",", ""))
            if num >= 1000000:
                return f"***万元"
            elif num >= 10000:
                return f"***元"
            else:
                return "***"
        except ValueError:
            return "***"


# 默认脱敏器实例
_default_masker = DataMasker()

# 预设常用规则
_default_masker.add_rule(MaskRule("phone", MaskType.PHONE))
_default_masker.add_rule(MaskRule("mobile", MaskType.PHONE))
_default_masker.add_rule(MaskRule("phone_number", MaskType.PHONE))
_default_masker.add_rule(MaskRule("id_card", MaskType.ID_CARD))
_default_masker.add_rule(MaskRule("id_number", MaskType.ID_CARD))
_default_masker.add_rule(MaskRule("bank_card", MaskType.BANK_CARD))
_default_masker.add_rule(MaskRule("card_number", MaskType.BANK_CARD))
_default_masker.add_rule(MaskRule("email", MaskType.EMAIL))
_default_masker.add_rule(MaskRule("name", MaskType.NAME))
_default_masker.add_rule(MaskRule("real_name", MaskType.NAME))
_default_masker.add_rule(MaskRule("address", MaskType.ADDRESS))


def get_masker() -> DataMasker:
    """获取默认脱敏器"""
    return _default_masker


def mask_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """便捷脱敏函数"""
    return _default_masker.mask_dict(data)


def mask_list_data(data_list: List[Dict]) -> List[Dict]:
    """便捷列表脱敏函数"""
    return _default_masker.mask_list(data_list)


def mask_phone(phone: str) -> str:
    """脱敏手机号"""
    return DataMasker._mask_phone(phone)


def mask_id_card(id_card: str) -> str:
    """脱敏身份证"""
    return DataMasker._mask_id_card(id_card)


def mask_email(email: str) -> str:
    """脱敏邮箱"""
    return DataMasker._mask_email(email)


def mask_name(name: str) -> str:
    """脱敏姓名"""
    return DataMasker._mask_name(name)
