namespace HelloWorldMaui;

public partial class MainPage : ContentPage
{
    public MainPage()
    {
        InitializeComponent();
    }

    private void OnButtonClicked(object sender, EventArgs e)
    {
        HelloLabel.Text = "Hello World!";
    }
}
