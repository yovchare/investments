export interface Account {
  account_id: number;
  account_name: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface AccountCreate {
  account_name: string;
  description?: string;
}

export interface AccountUpdate {
  account_name?: string;
  description?: string;
}

export interface Ticker {
  ticker_id: number;
  ticker_symbol: string;
  created_at: string;
  updated_at: string;
}

export interface TickerCreate {
  ticker_symbol: string;
}

export interface TickerUpdate {
  ticker_symbol?: string;
}

export interface TickerPrice {
  price_id: number;
  ticker_id: number;
  date: string;
  price: number;
  created_at: string;
  updated_at: string;
}

export interface TickerPriceCreate {
  ticker_id: number;
  date: string;
  price: number;
}

export interface TickerPriceUpdate {
  ticker_id?: number;
  date?: string;
  price?: number;
}

export type OwnershipStatus = 'Owned' | 'Unowned' | 'Unvested';

export interface AccountHolding {
  holding_id: number;
  account_id: number;
  date: string;
  ticker_symbol: string;
  number_of_shares: number;
  value: number;
  ownership: OwnershipStatus;
  created_at: string;
  updated_at: string;
}

export interface AccountHoldingCreate {
  account_id: number;
  date: string;
  ticker_symbol: string;
  number_of_shares: number;
  value: number;
  ownership: OwnershipStatus;
}

export interface AccountHoldingUpdate {
  account_id?: number;
  date?: string;
  ticker_symbol?: string;
  number_of_shares?: number;
  value?: number;
  ownership?: OwnershipStatus;
}

export interface Property {
  property_id: number;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface PropertyCreate {
  name: string;
}

export interface PropertyUpdate {
  name?: string;
}

export interface PropertyValue {
  property_value_id: number;
  property_id: number;
  date: string;
  valuation: number;
  created_at: string;
  updated_at: string;
}

export interface PropertyValueCreate {
  property_id: number;
  date: string;
  valuation: number;
}

export interface PropertyValueUpdate {
  property_id?: number;
  date?: string;
  valuation?: number;
}

export interface PropertyMortgage {
  property_mortgage_id: number;
  property_id: number;
  date: string;
  mortgage: number;
  created_at: string;
  updated_at: string;
}

export interface PropertyMortgageCreate {
  property_id: number;
  date: string;
  mortgage: number;
}

export interface PropertyMortgageUpdate {
  property_id?: number;
  date?: string;
  mortgage?: number;
}
