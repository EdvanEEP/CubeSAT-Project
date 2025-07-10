% === Sabit Sistem Parametreleri ===
Pt_dBm = 10 + 30 - 6;     % USRP çıkışı + PA kazancı - pad kaybı = 34 dBm
Gt_dB = 20;               % Ground antenna gain
Gr_dB = 0;                % CubeSat antenna gain
f_GHz = 0.437;            % Frequency in GHz
d_km = 300;               % Distance to satellite
rainLoss_dB = 2;          % Atmospheric loss
systemLoss_dB = 1;        % Cable/system loss
padLoss_dB = 6;           % Impedance matching pad loss
k = 1.38e-23;             % Boltzmann constant
T = 290;                  % Standard temperature in K
BW = 100e3;               % Bandwidth (100 kHz)

% === FSPL hesapla ===
FSPL_dB = 20*log10(d_km) + 20*log10(f_GHz) + 92.45;
totalLoss_dB = FSPL_dB + rainLoss_dB + systemLoss_dB;

% === EIRP hesapla ===
EIRP_dBm = Pt_dBm + Gt_dB;

% === Alınan Güç (Pr) ===
Pr_dBm = EIRP_dBm - totalLoss_dB + Gr_dB;

% === Gürültü Gücü (Pn) ===
Pn_W = k * T * BW;
Pn_dBm = 10*log10(Pn_W) + 30;

% === SNR ve BER ===
SNR_dB = Pr_dBm - Pn_dBm;
SNR_linear = 10^(SNR_dB/10);
BER = qfunc(sqrt(2 * SNR_linear));

% === Sonuçları yazdır ===
fprintf('--- RF Link Budget Outputs ---\n');
fprintf('Bandwidth (BW)         = %.0f kHz\n', BW / 1e3);
fprintf('EIRP                   = %.2f dBm\n', EIRP_dBm);
fprintf('Free Space Path Loss   = %.2f dB\n', FSPL_dB);
fprintf('Total Link Loss        = %.2f dB\n', totalLoss_dB);
fprintf('Received Power (Pr)    = %.2f dBm\n', Pr_dBm);
fprintf('Noise Power (Pn)       = %.2f dBm\n', Pn_dBm);
fprintf('SNR                    = %.2f dB\n', SNR_dB);
fprintf('BER (QPSK)             = %.2e\n', BER);
