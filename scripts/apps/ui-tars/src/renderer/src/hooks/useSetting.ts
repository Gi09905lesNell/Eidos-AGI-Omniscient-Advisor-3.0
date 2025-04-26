/*
 * Copyright (c) 2025 Bytedance, Inc. and its affiliates.
 * SPDX-License-Identifier: Apache-2.0
 */
import { LocalStore } from '@main/store/validate';
import { useEffect, useState } from 'react';

export function useSetting() {
  const settingRpc = window.electron.setting;
  const [settings, setSettings] = useState<Partial<LocalStore>>({});

  useEffect(() => {
    const initSetting = async () => {
      const currentSetting = await settingRpc.getSetting();
      setSettings(currentSetting);
    };

    settingRpc.onUpdate((newState) => {
      setSettings(newState);
    });

    initSetting();

    // FIXME: clear setting update listener
  }, []);

  const {
    updateSetting,
    clearSetting,
    updatePresetFromRemote,
    importPresetFromText,
    importPresetFromUrl,
  } = settingRpc;

  return {
    settings,
    updateSetting,
    clearSetting,
    updatePresetFromRemote,
    importPresetFromText,
    importPresetFromUrl,
  };
}
