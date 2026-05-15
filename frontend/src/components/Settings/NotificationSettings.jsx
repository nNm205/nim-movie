import SettingsSection from "./SettingsSection";
import ToggleSwitch from "./ToggleSwitch";
import { useSettings } from "../../context/SettingsContext";

const NotificationSettings = () => {
  const { emailNotifications, setEmailNotifications } = useSettings();

  return (
    <SettingsSection title="Thông báo">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-white font-semibold">Email thông báo</h3>

          <p className="text-zinc-400 text-sm mt-1">
            Nhận email về phim mới và xu hướng
          </p>
        </div>

        <ToggleSwitch
          enabled={emailNotifications}
          onChange={setEmailNotifications}
        />
      </div>
    </SettingsSection>
  );
};

export default NotificationSettings;
