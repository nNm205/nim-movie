import Layout from "../components/Common/Layout";
import LanguageSettings from "../components/Settings/LanguageSettings";
import PlaybackSettings from "../components/Settings/PlaybackSettings";
import NotificationSettings from "../components/Settings/NotificationSettings";

const SettingsPage = () => {
  return (
    <Layout>
      <div className="bg-black text-white min-h-screen">
        <div className="max-w-5xl mx-auto px-4 py-10">
          <div className="mb-10">
            <h1 className="text-4xl font-bold">Cài đặt</h1>
          </div>

          <div className="space-y-8">
            <LanguageSettings />

            <PlaybackSettings />

            <NotificationSettings />
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default SettingsPage;
