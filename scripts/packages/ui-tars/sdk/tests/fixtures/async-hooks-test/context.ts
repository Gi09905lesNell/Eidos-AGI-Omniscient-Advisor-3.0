/*
 * Copyright (c) 2025 Bytedance, Inc. and its affiliates.
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncLocalStorage } from 'async_hooks';
import { FACTOR } from '../../../src/constants';

const instanceStorage = new AsyncLocalStorage<any>();

export function setCurrentInstance(instance: any) {
  return instanceStorage.enterWith(instance);
}

export function getCurrentInstance(): any {
  const instance = instanceStorage.getStore();
  if (!instance) {
    throw new Error('No instance found in current context');
  }
  return instance;
}

// ConfigContext 实现
export class ConfigContext {
  private static instance: ConfigContext;
  private configs = new WeakMap<any, Record<string, any>>();

  static getInstance(): ConfigContext {
    if (!ConfigContext.instance) {
      ConfigContext.instance = new ConfigContext();
    }
    return ConfigContext.instance;
  }

  setConfig(instance: any, config: Record<string, any>) {
    this.configs.set(instance, config);
  }

  getConfig(instance: any): Record<string, any> | null {
    return this.configs.get(instance) || null;
  }
}

export function useConfig(): Record<string, any> {
  const currentInstance = getCurrentInstance();
  const config = ConfigContext.getInstance().getConfig(currentInstance);
  if (!config) {
    console.error('Config not initialized');
    return {
      logger: console,
      factor: FACTOR,
    };
  }
  return config;
}
