/**
 * Copyright (c) 2025 Bytedance, Inc. and its affiliates.
 * SPDX-License-Identifier: Apache-2.0
 */
import os from 'node:os';

import { screen } from 'electron';

import { UTIO, UTIOPayload } from '@ui-tars/utio';

import { logger } from '../logger';
import { SettingStore } from '@main/store/setting';

export class UTIOService {
  private static instance: UTIOService;
  private utio: UTIO | null = null;

  static getInstance(): UTIOService {
    if (!UTIOService.instance) {
      UTIOService.instance = new UTIOService();
    }
    return UTIOService.instance;
  }

  private getEndpoint(): string | undefined {
    const endpoint = SettingStore.getStore().utioBaseUrl;
    logger.debug('[UTIO] endpoint:', endpoint);
    return endpoint;
  }

  private ensureUTIO() {
    const endpoint = this.getEndpoint();
    if (endpoint && !this.utio) {
      this.utio = new UTIO(endpoint);
    }
    return this.utio;
  }

  async appLaunched() {
    try {
      const utio = this.ensureUTIO();
      if (utio) {
        const primaryDisplay = screen.getPrimaryDisplay();
        const { width, height } = primaryDisplay.size;
        const payload: UTIOPayload<'appLaunched'> = {
          type: 'appLaunched',
          platform: process.platform,
          osVersion: os.release(),
          screenWidth: width,
          screenHeight: height,
        };

        logger.debug('[UTIO] payload:', payload);
        await utio.send(payload);
      }
    } catch (error) {
      logger.error('[UTIO] error:', error);
      throw error;
    }
  }

  async sendInstruction(instruction: string) {
    try {
      const utio = this.ensureUTIO();
      if (utio) {
        const payload: UTIOPayload<'sendInstruction'> = {
          type: 'sendInstruction',
          instruction,
        };
        logger.debug('[UTIO] payload:', payload);
        await utio.send(payload);
      }
    } catch (error) {
      logger.error('[UTIO] error:', error);
      throw error;
    }
  }

  async shareReport(params: {
    instruction: string;
    lastScreenshot?: string;
    report?: string;
  }) {
    try {
      const utio = this.ensureUTIO();
      if (utio) {
        const payload: UTIOPayload<'shareReport'> = {
          type: 'shareReport',
          ...params,
        };
        logger.debug('[UTIO] payload:', payload);
        await utio.send(payload);
      }
    } catch (error) {
      logger.error('[UTIO] error:', error);
      throw error;
    }
  }
}
