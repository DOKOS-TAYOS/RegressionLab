# Troubleshooting

This guide covers known issues, common problems, and their solutions. It also includes information about future updates and the development roadmap.

## Common Problems and Solutions

### Installation Issues

#### Problem: Python Not Found

```
'python' is not recognized as an internal or external command
```

**Solution**:
1. Verify Python installation: Open Command Prompt/Terminal.
2. Try `python --version` or `python3 --version`.
3. If not found, install Python from [python.org](https://python.org).
4. **Important**: During installation, check "Add Python to PATH".
5. Restart terminal after installation.

#### Problem: Virtual Environment Not Found (bin launchers)

```
ERROR: Virtual environment not found
Please run setup.bat first
```
(or `setup.sh` on macOS/Linux)

**Solution**: The `bin/` launchers (`run.bat`, `run.sh`, `run_streamlit.bat`, `run_streamlit.sh`, `run_tests.bat`, `run_tests.sh`) require a project virtual environment. From the project root, run:
- **Windows**: `setup.bat`
- **macOS/Linux**: `chmod +x setup.sh` then `./setup.sh`

Then run the desired launcher again.

#### Problem: Permission Denied on Linux/macOS

```
Permission denied: ./install.sh
```

**Solution**:
```bash
chmod +x install.sh
chmod +x setup.sh
chmod +x bin/run.sh
chmod +x bin/run_streamlit.sh
./install.sh
```

#### Problem: Virtual Environment Won't Activate (Windows PowerShell)

```
cannot be loaded because running scripts is disabled on this system
```

**Solution**:
1. Open PowerShell as Administrator.
2. Run: `Set-ExecutionPolicy RemoteSigned`.
3. Confirm with 'Y'.
4. Retry activation: `.venv\Scripts\Activate.ps1`.

#### Problem: Module Not Found After Installation

```
ModuleNotFoundError: No module named 'numpy'
```

**Solution**:
1. Ensure virtual environment is activated.
   - You should see `(.venv)` in your terminal prompt.
   - Windows: `.venv\Scripts\activate`.
   - macOS/Linux: `source .venv/bin/activate`.
2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Verify installation:
   ```bash
   pip list | grep numpy
   ```

### Data Loading Issues

#### Problem: "File not found" Error

**Solution**:
1. Check file exists in specified location.
2. Use absolute path if relative path fails.
3. Check file permissions (read access required).
4. Verify file extension (.csv, .xlsx, .txt).

#### Problem: CSV File Appears Empty

**Solution**:
1. Open file in text editor to verify content.
2. Check delimiter (comma, semicolon, tab).
3. Ensure first row contains column headers.
4. Remove any blank lines at beginning of file.

#### Problem: Excel File Won't Load

**Solution**:
1. Ensure `openpyxl` is installed: `pip install openpyxl`.
2. Check file isn't password-protected.
3. Verify file isn't corrupted (try opening in Excel).
4. Save as .xlsx format (newer format more reliable).

#### Problem: Uncertainty Columns Not Detected

**Solution**:
1. Verify naming: uncertainty for column `x` must be named `ux`.
2. Use lowercase `u` prefix.
3. Check for extra spaces in column names.
4. Ensure uncertainty columns contain numeric values.

### Fitting Issues

#### Problem: "Optimal parameters not found"

```
RuntimeError: Optimal parameters not found
```

**Causes**:
- Not enough data points (need at least 5-10).
- Data doesn't match equation type.
- Bad initial parameter guess.
- Equation too complex for data.

**Solutions**:
1. **Check data quality**:
   - Plot data first (use "Watch Data").
   - Look for obvious outliers.
   - Ensure sufficient data points.

2. **Try different equation**:
   - Start with simpler equations (linear, quadratic).
   - Use Checker mode to test multiple equations.

3. **Provide better initial guess**:
   - For custom formulas, estimate parameters manually.
   - Look at data range to guess amplitudes.

4. **Simplify the model**:
   - Reduce number of parameters.
   - Remove unnecessary complexity.


#### Problem: Low R² Value (Poor Fit)

**Causes**:
- Wrong equation type for data.
- Noisy data.
- Outliers present.
- Insufficient data points.

**Solutions**:
1. **Try different equations**:
   - Use Checker or Total Fitting mode.
   - Compare R² values across equations.

2. **Clean data**:
   - Use Loop mode to iteratively remove outliers.
   - Filter data before fitting.

3. **Check for systematic issues**:
   - Is there a trend the equation doesn't capture?
   - Are there periodic components?
   - Is data actually stochastic?


#### Problem: Parameters Have Huge Uncertainties

```
a = 2.5 ± 10.3  (uncertainty > parameter value!)
```

**Causes**:
- Poorly conditioned problem.
- Parameters are correlated.
- Not enough data to constrain parameters.
- Wrong equation type.

**Solutions**:
1. **Collect more data**: More points reduce uncertainties.
2. **Extend data range**: Cover wider range of X values.
3. **Reduce parameters**: Simpler model may be better.
4. **Fix some parameters**: If you know certain values, fix them.

### Plotting Issues

#### Problem: Plot Window is Blank

**Solution**:
1. Check output directory exists and is writable.
2. Verify matplotlib is installed: `pip install matplotlib`.
3. Check logs for error messages: `regressionlab.log`.
4. Try recreating virtual environment.

#### Problem: Plot Quality is Poor

**Solution**:
1. Increase DPI in `.env`:
   ```ini
   DPI=300  # For high-quality plots
   ```
2. Adjust figure size:
   ```ini
   PLOT_FIGSIZE_WIDTH=12
   PLOT_FIGSIZE_HEIGHT=6
   ```
3. Modify font sizes in `.env`.

#### Problem: Error Bars Don't Appear

**Solution**:
1. Verify uncertainty columns exist and are named correctly.
2. Check uncertainties are non-zero.
3. Ensure uncertainties are numeric (not strings).
4. Try with test data to isolate issue.

### UI Issues (Tkinter)

#### Problem: Dialogs Don't Appear

**Solution**:
1. Check if dialog is behind main window (Alt+Tab).
2. Look in taskbar for new windows.
3. Disable "Always on top" if using other applications.
4. Restart application.

#### Problem: Buttons/Text Too Small or Large

**Solution**:
Edit `.env` file:
```ini
UI_FONT_SIZE=16  # Increase for larger text
UI_BUTTON_WIDTH=15  # Increase for wider buttons
```
Restart application.

#### Problem: Colors Are Unreadable

**Solution**:
Reset to default theme:
1. Copy `.env.example` to `.env`
2. Or manually set high-contrast colors:
   ```ini
   UI_BACKGROUND="white"
   UI_FOREGROUND="black"
   ```
3. Restart application.

### Streamlit Issues

#### Problem: Upload Fails Silently

**Solution**:
1. Check file size (< 200 MB for online version).
2. Verify file format (CSV, XLSX, TXT).
3. Clear browser cache and retry.
4. Try different browser.
5. Check browser console for JavaScript errors (F12).

#### Problem: Results Disappear After Refresh

**Solution**:
- This is expected behavior - Streamlit doesn't persist results.
- Download plots before refreshing.
- Use Tkinter version if persistence needed.

#### Problem: App is Slow/Unresponsive

**Solution**:
1. Close other tabs to free memory.
2. Use local version for better performance.
3. Reduce dataset size.
4. Avoid Total Fitting mode for large datasets.

## Debugging Tips

### Enable Debug Logging

Edit `.env`:
```ini
LOG_LEVEL=DEBUG
LOG_CONSOLE=true
```

View logs:
```bash
# Real-time log viewing
tail -f regressionlab.log

# Windows
type regressionlab.log
```

### Check Python Environment

```bash
# Verify Python version
python --version  # Should be 3.12+

# Check virtual environment is activated
which python  # Should point to .venv

# List installed packages
pip list

# Check specific package version
pip show numpy
```

### Isolate the Problem

1. **Test with sample data**: Use files in `input/` folder.
2. **Test different modes**: Does issue occur in all modes?
3. **Test both interfaces**: Try Tkinter AND Streamlit.
4. **Minimal example**: Create simplest case that reproduces issue.

### Report a Bug

If you can't solve the issue, please report it on GitHub with:

1. **Version**: Check version in main menu or `config` (e.g. `config/constants.py`).
2. **Operating System**: Windows, macOS, or Linux (with version).
3. **Python Version**: Output of `python --version`.
4. **Steps to Reproduce**: Exact steps to trigger the issue.
5. **Expected Behavior**: What should happen.
6. **Actual Behavior**: What actually happens.
7. **Error Messages**: Full error message and traceback.
8. **Logs**: Relevant portions of `regressionlab.log`.
9. **Screenshots**: If UI-related.
10. **Sample Data**: If possible, include data file that triggers issue.

## Future Updates and Roadmap

### Version 0.9.2 (Q1 2026) - Planned

**Major Features**:
- 📊 **Enhanced Plotting**: Interactive plots, zoom, pan.
- 🔮 **Prediction Windows**: Input specific X values to get predicted Y values from fitted models.
- 📐 **Multidimensional Fitting**: Support for fitting functions with multiple independent variables (z = f(x, y)).
- 🔧 **Data Preprocessing Tools**: Data smoothing, filtering, and transformation utilities.

### Version 1.0.0 (Q1 2026) - Planned

**Major Features**:
- 📱 **Android Support**: Run RegressionLab on Android devices using Termux terminal emulator.

**Documentation**:
- Video tutorials.

### Long-Term Goals (2027+)

**Under Consideration**:
- Time-series analysis tools.
- Machine learning models (SVM, Random Forest, Neural Networks).
- Bayesian regression and uncertainty quantification.
- Automated model selection and comparison tools.

### How to Request Features

1. **Check existing issues**: Avoid duplicates.
2. **Open GitHub issue**: Use "Feature Request" template.
3. **Describe use case**: Why is this feature needed?
4. **Provide examples**: Show what you want to achieve.
5. **Be patient**: We're a one person team!

## Optimization Tips

### For Faster Fitting

1. **Use compiled Python**: Try PyPy for pure Python code.
2. **Reduce plot resolution**: Lower DPI for faster rendering.
3. **Disable logging**: Set `LOG_LEVEL=WARNING` in production.
4. **Use local version**: Avoid network latency.
5. **Close result windows**: Free memory between fits.

### For Better Accuracy

1. **Provide uncertainties**: Weighted fitting is more accurate.
2. **Use appropriate equation**: Don't over-complicate.
3. **Collect more data**: More points = better parameter estimates.
4. **Extend data range**: Cover full range of interest.


## Getting Help

### Resources

1. **Documentation**: Start here!
   - [User Guide](usage.md).
   - [Configuration Guide](configuration.md).
   - [API Documentation](api/index).

2. **Examples**: Check `input/` folder for sample datasets.

3. **GitHub**:
   - [Issues](https://github.com/DOKOS-TAYOS/RegressionLab/issues): Report bugs.
   - [Discussions](https://github.com/DOKOS-TAYOS/RegressionLab/discussions): Ask questions.

4. **Community**:
   - Share your analyses.
   - Contribute code.
   - Improve documentation.

### Contact

- **Email**: alejandro.mata.ali@gmail.com.
- **GitHub**: Open an issue for bugs/features.

---

*Document last updated: February 2026.*
*If you solved a problem not listed here, please contribute by opening a pull request!*
