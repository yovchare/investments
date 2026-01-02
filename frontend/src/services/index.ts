import apiClient from './api';
import {
  Account,
  AccountCreate,
  AccountUpdate,
  Ticker,
  TickerCreate,
  TickerUpdate,
  TickerPrice,
  TickerPriceCreate,
  TickerPriceUpdate,
  AccountHolding,
  AccountHoldingCreate,
  AccountHoldingUpdate,
  Property,
  PropertyCreate,
  PropertyUpdate,
  PropertyValue,
  PropertyValueCreate,
  PropertyValueUpdate,
  PropertyMortgage,
  PropertyMortgageCreate,
  PropertyMortgageUpdate,
} from '../types';

// Account Services
export const accountService = {
  getAll: () => apiClient.get<Account[]>('/accounts'),
  getById: (id: number) => apiClient.get<Account>(`/accounts/${id}`),
  create: (data: AccountCreate) => apiClient.post<Account>('/accounts', data),
  update: (id: number, data: AccountUpdate) => apiClient.put<Account>(`/accounts/${id}`, data),
  delete: (id: number) => apiClient.delete(`/accounts/${id}`),
};

// Ticker Services
export const tickerService = {
  getAll: () => apiClient.get<Ticker[]>('/tickers'),
  getById: (id: number) => apiClient.get<Ticker>(`/tickers/${id}`),
  create: (data: TickerCreate) => apiClient.post<Ticker>('/tickers', data),
  update: (id: number, data: TickerUpdate) => apiClient.put<Ticker>(`/tickers/${id}`, data),
  delete: (id: number) => apiClient.delete(`/tickers/${id}`),
};

// Ticker Price Services
export const tickerPriceService = {
  getAll: () => apiClient.get<TickerPrice[]>('/ticker-prices'),
  getByTickerId: (tickerId: number) => apiClient.get<TickerPrice[]>(`/ticker-prices/ticker/${tickerId}`),
  getById: (id: number) => apiClient.get<TickerPrice>(`/ticker-prices/${id}`),
  create: (data: TickerPriceCreate) => apiClient.post<TickerPrice>('/ticker-prices', data),
  update: (id: number, data: TickerPriceUpdate) => apiClient.put<TickerPrice>(`/ticker-prices/${id}`, data),
  delete: (id: number) => apiClient.delete(`/ticker-prices/${id}`),
};

// Account Holding Services
export const holdingService = {
  getAll: () => apiClient.get<AccountHolding[]>('/holdings'),
  getById: (id: number) => apiClient.get<AccountHolding>(`/holdings/${id}`),
  create: (data: AccountHoldingCreate) => apiClient.post<AccountHolding>('/holdings', data),
  update: (id: number, data: AccountHoldingUpdate) => apiClient.put<AccountHolding>(`/holdings/${id}`, data),
  delete: (id: number) => apiClient.delete(`/holdings/${id}`),
};

// Property Services
export const propertyService = {
  getAll: () => apiClient.get<Property[]>('/properties'),
  getById: (id: number) => apiClient.get<Property>(`/properties/${id}`),
  create: (data: PropertyCreate) => apiClient.post<Property>('/properties', data),
  update: (id: number, data: PropertyUpdate) => apiClient.put<Property>(`/properties/${id}`, data),
  delete: (id: number) => apiClient.delete(`/properties/${id}`),
};

// Property Value Services
export const propertyValueService = {
  getAll: () => apiClient.get<PropertyValue[]>('/property-values'),
  getById: (id: number) => apiClient.get<PropertyValue>(`/property-values/${id}`),
  create: (data: PropertyValueCreate) => apiClient.post<PropertyValue>('/property-values', data),
  update: (id: number, data: PropertyValueUpdate) => apiClient.put<PropertyValue>(`/property-values/${id}`, data),
  delete: (id: number) => apiClient.delete(`/property-values/${id}`),
};

// Property Mortgage Services
export const propertyMortgageService = {
  getAll: () => apiClient.get<PropertyMortgage[]>('/property-mortgages'),
  getById: (id: number) => apiClient.get<PropertyMortgage>(`/property-mortgages/${id}`),
  create: (data: PropertyMortgageCreate) => apiClient.post<PropertyMortgage>('/property-mortgages', data),
  update: (id: number, data: PropertyMortgageUpdate) => apiClient.put<PropertyMortgage>(`/property-mortgages/${id}`, data),
  delete: (id: number) => apiClient.delete(`/property-mortgages/${id}`),
};

// Backup Services
export const backupService = {
  backup: (backupDir: string = '../data') => apiClient.post('/backup/backup', null, { params: { backup_dir: backupDir } }),
  restore: (backupDir: string = '../data') => apiClient.post('/backup/restore', null, { params: { backup_dir: backupDir } }),
};
