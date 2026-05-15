import SettingsSection from "./SettingsSection";
import ToggleSwitch from "./ToggleSwitch";
import { useSettings } from "../../context/SettingsContext";

const PlaybackSettings = () => {
  const { autoplayTrailer, setAutoplayTrailer, blurBackdrop, setBlurBackdrop } =
    useSettings();

  return (
    <SettingsSection title="Trình phát">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-white font-semibold">Tự động phát trailer</h3>

            <p className="text-zinc-400 text-sm mt-1">
              Trailer sẽ tự động phát khi mở trang phim
            </p>
          </div>

          <ToggleSwitch
            enabled={autoplayTrailer}
            onChange={setAutoplayTrailer}
          />
        </div>

        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-white font-semibold">Hiệu ứng nền mờ</h3>

            <p className="text-zinc-400 text-sm mt-1">
              Bật hiệu ứng làm mờ cho backdrop phim
            </p>
          </div>

          <ToggleSwitch enabled={blurBackdrop} onChange={setBlurBackdrop} />
        </div>
      </div>
    </SettingsSection>
  );
};

export default PlaybackSettings;
